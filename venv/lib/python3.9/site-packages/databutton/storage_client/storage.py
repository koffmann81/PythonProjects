import hashlib
import http
import json
import tempfile
from abc import ABC
from collections.abc import Iterable
from enum import Enum
from typing import Any, Optional

import httpx
import pandas as pd
from pydantic import BaseModel

from databutton.utils import get_api_url, get_auth_token, get_databutton_project_id
from databutton.utils.utctime import utc_now_str


class ContentTypes(str, Enum):
    arrow = "vnd.apache.arrow.file"
    json = "application/json"
    text = "text/plain"
    binary = "application/octet-stream"


class ContentShape(BaseModel):
    numberOfRows: int
    numberOfProperties: int


class Serializer(ABC):
    content_type: str = ContentTypes.binary

    def content_shape_of(self, value: Any) -> Optional[ContentShape]:
        return None

    def encode(self, value: Any) -> Iterable[bytes]:
        raise NotImplementedError("Must be implemented by serializer.")

    def decode(self, data: Iterable[bytes]) -> Any:
        raise NotImplementedError("Must be implemented by serializer.")


class BinarySerializer(Serializer):
    content_type = ContentTypes.binary

    def encode(self, value: bytes) -> Iterable[bytes]:
        yield value

    def decode(self, data: Iterable[bytes]) -> bytes:
        return b"".join(data)


class TextSerializer(Serializer):
    content_type = ContentTypes.text

    def encode(self, value: str) -> Iterable[bytes]:
        yield value.encode("utf8")

    def decode(self, data: Iterable[bytes]) -> str:
        return b"".join(data).decode(encoding="utf8", errors="strict")


class JsonSerializer(Serializer):
    content_type = ContentTypes.json

    def encode(self, value: dict) -> Iterable[bytes]:
        yield json.dumps(value).encode("utf8")

    def decode(self, data: Iterable[bytes]) -> dict:
        return json.loads(b"".join(data))


# Fallback if the spooledtemporaryfile thing doesn't work
# class DataFrameSerializer(Serializer):
#     content_type = ContentTypes.arrow
#
#     def content_shape_of(self, value: pd.DataFrame) -> Optional[ContentShape]:
#         return ContentShape(shape=value.shape)
#
#     def encode(self, value: pd.DataFrame) -> Iterable[bytes]:
#         buf = io.BytesIO()
#         value.to_feather(buf)
#         yield buf.getvalue()
#
#     def decode(self, data: Iterable[bytes]) -> pd.DataFrame:
#         return pd.read_feather(io.BytesIO(b''.join(data)))


class DataFrameSerializer(Serializer):
    content_type = ContentTypes.arrow

    def content_shape_of(self, value: pd.DataFrame) -> Optional[ContentShape]:
        rows, cols = value.shape
        return ContentShape(numberOfRows=rows, numberOfProperties=cols)

    def encode(self, value: pd.DataFrame) -> Iterable[bytes]:
        with tempfile.SpooledTemporaryFile(mode="w+b") as f:
            # Serialize entire file, possibly to file if it's large
            value.to_feather(f)
            f.seek(0)
            chunksize = 1024 * 1024
            while chunk := f.read(chunksize):
                yield chunk

    def decode(self, data: Iterable[bytes]) -> pd.DataFrame:
        with tempfile.SpooledTemporaryFile(mode="w+b") as f:
            for chunk in data:
                f.write(chunk)
            f.seek(0)
            df = pd.read_feather(f)
            return df


class CommitGetRef(BaseModel):
    dataKey: str
    contentType: str
    md5: str


class CommitPutRef(BaseModel):
    blobKey: str
    dataKey: str
    contentType: str
    md5: str
    size: int


class CommitRequest(BaseModel):
    getRefs: list[CommitGetRef]
    putRefs: list[CommitPutRef]


def hash_bytes_iter(
    bytes_iter: Iterable[bytes], hasher: Any, size: list[int], max_size: Optional[int]
) -> Iterable[bytes]:
    if len(size) != 1:
        raise ValueError("Pass list with size 1 to get size back")
    size[0] = 0
    for chunk in bytes_iter:
        size[0] += len(chunk)
        if max_size is not None and size[0] > max_size:
            raise Exception("Receiving too much data!")
        hasher.update(chunk)
        yield chunk


class RawStorage:
    """Orchestrate storage of metadata and byte contents on two different stores."""

    def __init__(
        self,
    ):
        self._project_id = None

    def _init(self):
        if self._project_id is None:
            self._project_id = get_databutton_project_id()
            self._dbapi_url = get_api_url(self._project_id)

            # Workaround for local testing:
            self._projectid_param_for_tests = ""
            if self._dbapi_url.startswith("http://localhost"):
                self._projectid_param_for_tests = f"?project={self._project_id}"

    def _auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {get_auth_token()}",
        }

    def upload(self, data_key: str, value: object, serializer: Serializer):
        self._init()

        # Encode in target byte format
        encoded_bytes_iter = serializer.encode(value)

        # Iterate over chunks of response, hashing and
        # counting bytes in chunks while decoding
        hashalg = hashlib.md5()
        byte_count = [0]
        bytes_iter = hash_bytes_iter(
            encoded_bytes_iter, hashalg, byte_count, max_size=None
        )

        # To implement client side encryption we would add this here:
        # 1. generate a random dek (data encryption key)
        # dek = generate_key()
        # 2. encrypt dek with a call to a databutton-keyring service wrapping kms
        # encrypted_dek = encrypt_key(dek)
        # 3. encrypt bytes_value with dek before storing in blob
        # bytes_value = encrypt_user_data(bytes_value, encryption_key)
        # 4. store encrypted dek in metadata

        content_type = serializer.content_type
        content_shape = serializer.content_shape_of(value)

        # TODO: Get userId/systemId from auth token or environment.
        #       I.e. which user called, which job is running.
        user_id: Optional[str] = None
        system_id = "databutton"

        with httpx.Client() as client:
            # [1/3] Send metadata to db-api to prepare for blob upload
            prepare_request = {
                "generateUrl": True,
                "dataKey": data_key,
                "contentType": content_type,
            }
            if user_id is not None:
                prepare_request["uploadedBy"] = {
                    "timestamp": utc_now_str(),
                    "type": "user",
                    "id": user_id,
                    # "name" if we can get it from token?
                }
            else:
                prepare_request["uploadedBy"] = {
                    "timestamp": utc_now_str(),
                    "type": "system",
                    "id": system_id,
                }
            # Extra metadata for dataframes:
            if content_shape is not None:
                prepare_request["contentShape"] = content_shape.dict()

            resp = client.post(
                url=f"{self._dbapi_url}/storage/prepare{self._projectid_param_for_tests}",
                headers={
                    "Authorization": f"Bearer {get_auth_token()}",
                },
                json=prepare_request,
            )
            if resp.status_code != http.HTTPStatus.OK:
                raise Exception(
                    f"Upload preparations for '{data_key}' failed, status_code={resp.status_code}"
                )
            prepare_response = resp.json()
            blob_key = prepare_response["blobKey"]
            signed_url = prepare_response["signedUrl"]

            # [2/3] Store in blob storage
            resp = client.put(
                url=signed_url,
                headers={
                    "Content-Type": content_type,
                },
                content=bytes_iter,
            )
            if resp.status_code != http.HTTPStatus.OK:
                raise Exception(
                    f"Upload of '{data_key}' failed, status_code={resp.status_code}"
                )

            # Compute checksum
            md5_hash = hashalg.hexdigest()
            size = byte_count[0]

            # [3/3] Commit data to become the current version
            # Note: To implement transactions, we'll need to save up commit data
            #       on each get and put within transaction scope and delay this
            #       commit call to when committing the transaction
            get_refs = []
            put_refs = [
                CommitPutRef(
                    blobKey=blob_key,
                    dataKey=data_key,
                    contentType=content_type,
                    md5=md5_hash,
                    size=size,
                )
            ]
            resp = client.post(
                url=f"{self._dbapi_url}/storage/commit{self._projectid_param_for_tests}",
                headers={
                    "Authorization": f"Bearer {get_auth_token()}",
                },
                json=CommitRequest(
                    getRefs=get_refs,
                    putRefs=put_refs,
                ).dict(),
            )
            if resp.status_code != http.HTTPStatus.OK:
                raise Exception(
                    f"Upload commit for '{data_key}' failed, status_code={resp.status_code}"
                )
            written = resp.json().get("written")
            if written != 1:
                raise Exception(f"API responds {written} files written, expected 1")

        # Done uploading!

    def download(self, data_key: str, serializer: Serializer) -> Optional[object]:
        self._init()

        content_type = serializer.content_type

        # Get metadata and download url for current version from db-api
        with httpx.Client() as client:
            resp = client.post(
                url=f"{self._dbapi_url}/storage/geturl{self._projectid_param_for_tests}",
                headers={
                    "Authorization": f"Bearer {get_auth_token()}",
                },
                json={
                    "dataKey": data_key,
                    "contentType": content_type,
                },
            )
            if resp.status_code == http.HTTPStatus.NOT_FOUND:
                return None
            if resp.status_code != http.HTTPStatus.OK:
                raise Exception(
                    f"Download preparations for '{data_key}' failed, status_code={resp.status_code}"
                )
            geturl_response = resp.json()
            signed_url = geturl_response["signedUrl"]
            md5_hash = geturl_response["md5"]
            size = geturl_response["size"]

            # Note: To implement transactions, need to collect CommitGetRefs
            #       here if we are in an active transaction
            # get_ref = CommitGetRef(
            #     dataKey=data_key,
            #     contentType=content_type,
            #     md5=md5_hash,
            # )

            # Get the bytes from blob store
            resp = client.get(url=signed_url)
            if resp.status_code == http.HTTPStatus.NOT_FOUND:
                return None
            if resp.status_code != http.HTTPStatus.OK:
                raise Exception(
                    f"Download of '{data_key}' failed, status_code={resp.status_code}, url={signed_url}"
                )

            # Iterate over chunks of response, hashing and
            # counting bytes in chunks while decoding
            hashalg = hashlib.md5()
            byte_count = [0]
            bytes_iter = hash_bytes_iter(resp.iter_bytes(), hashalg, byte_count, size)

            # To implement client side encryption we would add this here:
            # 1. get encrypted dek (data encryption key) from geturl metadata
            # 2. decrypt dek with a call to a databutton-keyring service wrapping kms
            # 3. decrypt bytes_value with dek
            # if encrypted_dek is not None:
            #     bytes_value = decrypt_user_data(encrypted_dek, bytes_value, aad=something)

            # Decode from byte chunks
            value = serializer.decode(bytes_iter)

            # Sanity checking
            actual_size = byte_count[0]
            if size != actual_size:
                raise Exception(f"File sizes do not match: {size} != {actual_size}")
            actual_md5_hash = hashalg.hexdigest()
            if md5_hash != actual_md5_hash:
                raise Exception(
                    f"Checksums do not match: {md5_hash} != {actual_md5_hash}"
                )

        return value


class SerializedStorage:
    """Internal helper class for typed storage managers."""

    def __init__(
        self,
        *,
        raw_storage: RawStorage,
        serializer: Serializer,
    ):
        self._raw_storage = raw_storage
        self.serializer = serializer

    def put(self, key: str, value: Any):
        self._raw_storage.upload(
            data_key=key,
            value=value,
            serializer=self.serializer,
        )

    def get(self, key: str, *, default: Optional[Any] = None) -> Optional[Any]:
        value = self._raw_storage.download(
            data_key=key,
            serializer=self.serializer,
        )
        if value is None:
            if default is None:
                raise FileNotFoundError(f"Could not find {key}")
            if callable(default):
                return default()
            return default
        return value


class BinaryStorage:
    """Manage storage of raw binary files."""

    Serializer = BinarySerializer

    def __init__(self, *, raw_storage: RawStorage):
        self._store = SerializedStorage(
            raw_storage=raw_storage, serializer=self.Serializer()
        )

    def put(self, key: str, value: bytes):
        self._store.put(key=key, value=value)

    def get(self, key: str, *, default: Optional[bytes] = None) -> Optional[bytes]:
        return self._store.get(key=key, default=default)


class TextStorage:
    """Manage storage of plain text files."""

    Serializer = TextSerializer

    def __init__(self, *, raw_storage: RawStorage):
        self._store = SerializedStorage(
            raw_storage=raw_storage, serializer=self.Serializer()
        )

    def put(self, key: str, value: str):
        self._store.put(key=key, value=value)

    def get(self, key: str, *, default: Optional[str] = None) -> Optional[str]:
        return self._store.get(key=key, default=default)


class JsonStorage:
    """Manage storage of json files, assumed to be a dict on the python side."""

    Serializer = JsonSerializer

    def __init__(self, *, raw_storage: RawStorage):
        self._store = SerializedStorage(
            raw_storage=raw_storage, serializer=self.Serializer()
        )

    def put(self, key: str, value: dict):
        self._store.put(key=key, value=value)

    def get(self, key: str, *, default: Optional[dict] = None) -> Optional[dict]:
        return self._store.get(key=key, default=default)


class DataFramesStorage:
    """Manage storage of pandas dataframes as arrow files."""

    Serializer = DataFrameSerializer

    def __init__(self, *, raw_storage: RawStorage):
        self._store = SerializedStorage(
            raw_storage=raw_storage, serializer=self.Serializer()
        )

    def put(
        self,
        key: str,
        value: pd.DataFrame,
        *,
        persist_index: bool = False,
    ):
        if isinstance(key, pd.DataFrame) and isinstance(value, str):
            print("Deprecation warning: Swap put(value, key) -> put(key, value).")
            key, value = value, key
        if not persist_index:
            value = value.reset_index(drop=True)
        self._store.put(key=key, value=value)
        return True  # From old implementation

    def get(
        self,
        key: str,
        *,
        ignore_not_found: bool = True,
        default: Optional[pd.DataFrame] = None,
    ) -> Optional[pd.DataFrame]:
        if default is None and ignore_not_found is True:

            def empty_dataframe() -> pd.DataFrame:
                return pd.DataFrame()

            default = empty_dataframe
        return self._store.get(key=key, default=default)

    def concat(
        self,
        key: str,
        other: pd.DataFrame,
        *,
        ignore_index: bool = False,
        verify_integrity: bool = False,
        sort: bool = False,
    ) -> pd.DataFrame:
        try:
            df = self.get(key=key, ignore_not_found=False)
        except FileNotFoundError:
            new_df = other
        else:
            new_df = pd.concat(
                [df, other],
                ignore_index=ignore_index,
                verify_integrity=verify_integrity,
                sort=sort,
            )
        self.put(key=key, value=new_df)
        return new_df

    def add(self, key: str, entry: Any) -> pd.DataFrame:
        return self.concat(
            key=key, other=pd.DataFrame(entry, index=[0]), ignore_index=True
        )

    def clear(self, key: str):
        """Empty the data at a certain key, leaving you with an empty dataframe on the next .get"""
        return self.put(key=key, value=pd.DataFrame(data=None).reset_index())


class StorageClient:
    def __init__(self):
        # How should we deal with dependency injection in general?
        self._raw_storage = RawStorage()

        self._binary = None
        self._text = None
        self._json = None
        self._dataframes = None

    @property
    def binary(self):
        """Store raw bytes."""
        if self._binary is None:
            self._binary = BinaryStorage(raw_storage=self._raw_storage)
        return self._binary

    @property
    def text(self):
        """Store plain text."""
        if self._text is None:
            self._text = TextStorage(raw_storage=self._raw_storage)
        return self._text

    @property
    def json(self):
        """Store basic python dicts as json."""
        if self._json is None:
            self._json = JsonStorage(raw_storage=self._raw_storage)
        return self._json

    @property
    def dataframes(self):
        """Store and retrieve pandas DataFrames."""
        if self._dataframes is None:
            self._dataframes = DataFramesStorage(raw_storage=self._raw_storage)
        return self._dataframes
