import datetime as dt
import streamlit as st
from data_processor import get_filtered_dataframe, generate_full_turnus_dataframe

# Get the full dataframe info for sidebar display

turnus, weeks = generate_full_turnus_dataframe()
numWeeks = len(turnus)

with st.sidebar:
  startDate = st.date_input(
  "Start Date",
  dt.datetime.today())
  endDate = st.date_input("End Date (default 12 weeks after start)", startDate + dt.timedelta(weeks=12))

```
st.write("Has data from 26.sep 2022 and "+str(numWeeks) +" weeks forward")
```

# Get filtered dataframe using the new function
