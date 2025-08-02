import datetime as dt
import streamlit as st
from data_processor import get_filtered_dataframe, generate_full_turnus_dataframe

# Get the full dataframe info for sidebar display
turnus, weeks = generate_full_turnus_dataframe()
numWeeks = len(turnus)

with st.sidebar:
    startDate = st.date_input(
        "Start Date",
        dt.datetime.today()
    )
    endDate = st.date_input(
        "End Date (default 12 weeks after start)",
        startDate + dt.timedelta(weeks=12)
    )

    st.write(f"Has data from 26. sep 2022 and {numWeeks} weeks forward")

# Get filtered dataframe using the new function
turnusStreamlit = get_filtered_dataframe(startDate, endDate)

# Display the dataframe
if not turnusStreamlit.empty:
    st.dataframe(turnusStreamlit, height=450)
else:
    st.warning("No data available for the selected date range. Please check your dates.")
