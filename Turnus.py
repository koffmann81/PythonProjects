import datetime as dt
import pandas as pd
import streamlit as st

#Empty list of 12 weeks
planUke1=["D", "D", "A2", "A2", "D", "F2", "F1"]
planUke2=["A", "D", "D", "D", "F2", "F2", "F1"]
planUke3=["D", "D", "D", "F1", "A", "D", "A"]
planUke4=["F2", "D", "A2", "A2", "F2", "F2", "F1"]
planUke5=["F2", "D", "A2", "D", "D", "F2", "F1"]
planUke6=["D", "D", "D", "A", "D", "F2", "F1"]
planUke7=["D", "D", "D", "A2", "D", "F2", "F1"]
planUke8=["A", "D", "A", "D", "D", "F2", "F1"]
planUke9=["D", "D", "D", "F1", "A", "D", "A"]
planUke10=["D", "F2", "D", "D", "F2", "F2" ,"F1"]
planUke11=["A", "D", "D", "D", "D", "F2", "F1"]
planUke12=["A", "D", "D", "D", "D", "F2", "F1"]
days=["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]

planListe=[]
planUker={1:planUke1, 2:planUke2, 3:planUke3, 4:planUke4, 5:planUke5, 6:planUke6, 7:planUke7, 8:planUke8, 9:planUke9, 10:planUke10, 11:planUke11, 12:planUke12}

dfPlan=pd.DataFrame(list(planUker.values()), columns=days)


numWeeks=200

turnusOverview=[]
#Hard Start
refMonday=dt.datetime(2022, 9,26)
refTuple=(1,refMonday)
turnusMapping=[]
planUkeNr=[]
ukeNr=[]
#turnusMapping.append(refTuple)

for i in range(numWeeks):
    ukeMandag=refMonday+dt.timedelta(days=7*i)
    ukeNr.append(ukeMandag.isocalendar()[1])
    if (i+1)%12==0:
        turnusOverview.append(planUker[12])
        addTuple = (12, refMonday + dt.timedelta(days=7 * i ))
        turnusMapping.append(addTuple)
        planUkeNr.append(12)
    else:
        turnusOverview.append(planUker[(i+1)%12])
        addTuple = ((i + 1)%12, refMonday + dt.timedelta(days=7 * i))
        turnusMapping.append(addTuple)
        planUkeNr.append((i+1)%12)

tuDf=pd.DataFrame(turnusOverview, columns=days)
#Function returning weekDates for a given Monday
def weekOutput(Monday):
    weekDates = []
    weekDates.append(Monday)
    for i in range(6):
        dayafter=weekDates[i] + dt.timedelta(days=1)
        weekDates.append(dayafter)
    weekDates = [x.strftime("%d/%m/%y") for x in weekDates]
    return weekDates

weeks=[]
weeks.append(weekOutput(refMonday))
weekRow=[]
weekRow.append(weeks[0][0]+" - "+weeks[0][6])
nextMonday=refMonday+dt.timedelta(days=7)
#test git

for i in range(numWeeks-1):
    weeks.append(weekOutput(nextMonday))
    weekRow.append(weeks[i+1][0]+" - "+weeks[i+1][6])
    nextMonday=nextMonday+dt.timedelta(days=7)

tuDf.index=weekRow
tuDf["Week Dates"]=weeks
tuDf["PlanUke"]=planUkeNr
tuDf["Uke"]=ukeNr
turnus=tuDf[["Uke","Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn", "PlanUke"]]
#turnus=tuDf.iloc[:,:7]
print(turnus)

startingDate=dt.datetime(2022, 9, 27).strftime("%d/%m/%y")
endDate=dt.datetime(2022, 12, 8).strftime("%d/%m/%y")

def startEndWeek(start, end):

    for i in range(len(weeks)):
        if start in weeks[i]:
            startIndex=i
        if end in weeks[i]:
            endIndex=i
    return (startIndex, endIndex)


with st.sidebar:
    startDate = st.date_input(
        "Start Date",
        dt.datetime.today())
    endDate = st.date_input("End Date (default 12 weeks after start)", startDate + dt.timedelta(weeks=12))
    startDateFormat=startDate.strftime("%d/%m/%y")
    endDateFormat=endDate.strftime("%d/%m/%y")
    a=startEndWeek(startDateFormat, endDateFormat)
    #st.write(a)
    st.write("Has data from 26.sep 2022 and "+str(numWeeks) +" weeks forward")
turnusStreamlit=turnus.iloc[a[0]:a[1], :9]
st.dataframe(turnusStreamlit, height=450)


#st.write(startEndWeek(startDate.strftime("%d/%m/%y"), endDate("%%d/%m/%y")))

#today=dt.datetime.today()
#today=today.strftime("%d/%m/%y")