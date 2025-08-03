import datetime as dt
import pandas as pd

# Shift schedule data
planUke1 = ["D", "D", "A2", "A2", "D", "F2", "F1"]
planUke2 = ["A", "D", "D", "D", "F2", "F2", "F1"]
planUke3 = ["D", "D", "D", "F1", "A", "D", "A"]
planUke4 = ["F2", "D", "A2", "A2", "F2", "F2", "F1"]
planUke5 = ["F2", "D", "A2", "D", "D", "F2", "F1"]
planUke6 = ["D", "D", "D", "A", "D", "F2", "F1"]
planUke7 = ["D", "D", "D", "A2", "D", "F2", "F1"]
planUke8 = ["A", "D", "A", "D", "D", "F2", "F1"]
planUke9 = ["D", "D", "D", "F1", "A", "D", "A"]
planUke10 = ["D", "F2", "D", "D", "F2", "F2", "F1"]
planUke11 = ["A", "D", "D", "D", "D", "F2", "F1"]
planUke12 = ["A", "D", "D", "D", "D", "F2", "F1"]

days = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
planUker = {
    1: planUke1, 2: planUke2, 3: planUke3, 4: planUke4, 5: planUke5, 6: planUke6,
    7: planUke7, 8: planUke8, 9: planUke9, 10: planUke10, 11: planUke11, 12: planUke12
}


def weekOutput(Monday):
    """Function returning weekDates for a given Monday"""
    weekDates = [Monday]
    for i in range(6):
        dayafter = weekDates[i] + dt.timedelta(days=1)
        weekDates.append(dayafter)
    weekDates = [x.strftime("%d/%m/%y") for x in weekDates]
    return weekDates


def startEndWeek(start, end, weeks):
    """Find start and end indices for date filtering"""
    startIndex = None
    endIndex = None
    for i in range(len(weeks)):
        if start in weeks[i]:
            startIndex = i
        if end in weeks[i]:
            endIndex = i
    return (startIndex, endIndex)


def generate_full_turnus_dataframe(numWeeks=300):
    """
    Generate the complete turnus dataframe
    """
    turnusOverview = []
    refMonday = dt.datetime(2022, 9, 26)
    turnusMapping = []
    planUkeNr = []
    ukeNr = []

    for i in range(numWeeks):
        ukeMandag = refMonday + dt.timedelta(days=7 * i)
        ukeNr.append(ukeMandag.isocalendar()[1])
        plan_index = 12 if (i + 1) % 12 == 0 else (i + 1) % 12
        turnusOverview.append(planUker[plan_index])
        turnusMapping.append((plan_index, ukeMandag))
        planUkeNr.append(plan_index)

    tuDf = pd.DataFrame(turnusOverview, columns=days)

    weeks = []
    weekRow = []
    nextMonday = refMonday

    for i in range(numWeeks):
        week_dates = weekOutput(nextMonday)
        weeks.append(week_dates)
        weekRow.append(week_dates[0] + " - " + week_dates[6])
        nextMonday += dt.timedelta(days=7)

    tuDf.index = weekRow
    tuDf["Week Dates"] = weeks
    tuDf["PlanUke"] = planUkeNr
    tuDf["Uke"] = ukeNr

    turnus = tuDf[["Uke", "Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn", "PlanUke"]]
    return turnus, weeks


def get_current_week_dataframe():
    """
    Get the current week’s schedule (for email)
    """
    turnus, weeks = generate_full_turnus_dataframe()
    today = dt.datetime.today()
    today_str = today.strftime("%d/%m/%y")

    current_week_index = None
    for i, week in enumerate(weeks):
        if today_str in week:
            current_week_index = i
            break

    if current_week_index is not None:
        return turnus.iloc[current_week_index:current_week_index + 4]
    else:
        return turnus.iloc[:4]


def get_filtered_dataframe(start_date, end_date):
    """
    Get dataframe filtered by date range (for Streamlit)
    """
    turnus, weeks = generate_full_turnus_dataframe()
    start_str = start_date.strftime("%d/%m/%y")
    end_str = end_date.strftime("%d/%m/%y")

    try:
        start_index, end_index = startEndWeek(start_str, end_str, weeks)
        if start_index is not None and end_index is not None:
            return turnus.iloc[start_index:end_index + 1]
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()


def format_dataframe_for_email(df):
    """
    Format dataframe for email
    """
    if df.empty:
        return "<p>No data available for the current period.</p>", "No data available."

    html_table = df.to_html(index=True, table_id="turnus-schedule", escape=False)

    html_content = f"""
    <style>
    table#turnus-schedule {{
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }}
    table#turnus-schedule th, table#turnus-schedule td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }}
    table#turnus-schedule th {{
        background-color: #f2f2f2;
        font-weight: bold;
    }}
    table#turnus-schedule tr:nth-child(even) {{
        background-color: #f9f9f9;
    }}
    .shift-code {{
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 4px;
    }}
    </style>
    <h3>Turnus Schedule</h3>
    {html_table}
    <p><strong>Total weeks:</strong> {len(df)}</p>
    <p><strong>Shift codes:</strong> D=Day, A=Afternoon230, A2=Afternoon120, F1=DayOff, F2=DayOff</p>
    """

    text_content = f"""
# TURNUS SCHEDULE

{df.to_string()}

Total weeks: {len(df)}
Shift codes: D=Day, A=AfternoonLate, A2=AfternoonEarly, F1=Off, F2=Off
"""
    return html_content, text_content


def get_schedule_summary(df):
    """
    Get summary statistics for the schedule
    """
    if df.empty:
        return {}

    shift_counts = {}
    for day in days:
        if day in df.columns:
            counts = df[day].value_counts()
            for shift, count in counts.items():
                shift_counts[shift] = shift_counts.get(shift, 0) + count

    return {
        "total_weeks": len(df),
        "shift_distribution": shift_counts,
        "date_range": f"{df.index[0]} to {df.index[-1]}" if len(df) > 0 else "No data"
    }
