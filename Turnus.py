import datetime as dt
import pandas as pd

#Empty list of 12 weeks
planUke1=["F2", "D", "A2", "A2", "D", "F2", "F1"]
planUke2=["A", "D", "D", "D", "F2", "F2", "F1"]
planUke3=["D", "D", "D", "F1", "A", "D", "A"]
planUke4=["D", "D", "A2", "A2", "F2", "F2", "F1"]
planUke5=["F2", "F2", "A2", "D", "D", "F2", "F1"]
planUke6=["D", "D", "D", "F1", "A", "A", "D"]
planUke7=["D", "D", "F2", "A2", "D", "F2", "F1"]
planUke8=["A", "D", "A", "D", "D", "F2", "F1"]
planUke9=["D", "D", "D", "F1", "A", "D", "A"]
planUke10=["D", "F2", "D", "D", "F2", "F2" ,"F1"]
planUke11=["A", "D", "D", "D", "D", "F2", "F1"]
planUke12=["A", "D", "F1", "D", "A", "A", "D"]
days=["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]

planListe=[]
planUker={1:planUke1, 2:planUke2, 3:planUke3, 4:planUke4, 5:planUke5, 6:planUke6, 7:planUke7, 8:planUke8, 9:planUke9, 10:planUke10, 11:planUke11, 12:planUke12}

dfPlan=pd.DataFrame(list(planUker.values()), columns=days)

#startDay=26
#startMonth=9
#startYear=2022
#startingPoint=dt.datetime(startYear, startMonth, startDay)
numWeeks=23

turnusOverview=[]
#Hard Start
refMonday=dt.datetime(2022, 9,26)

for i in range(numWeeks):
    if (i+1)%12==0:
        turnusOverview.append(planUker[12])
    else:
        turnusOverview.append(planUker[(i+1)%12])

tuDf=pd.DataFrame(turnusOverview, columns=days)
print(tuDf)
print(turnusOverview)

refTuple=(1,refMonday)
turnusMapping=[]
turnusMapping.append(refTuple)
numTuples=10
for i in range(numTuples-1):
    addTuple=(i+2,refMonday+dt.timedelta(days=7*(i+1)))
    turnusMapping.append(addTuple)

print(turnusMapping)

print(refTuple)

#Function returning weekDates for a given Monday
def weekOutput(Monday):
    weekDates = []
    weekDates.append(Monday)
    for i in range(6):
        dayafter=weekDates[i] + dt.timedelta(days=1)
        weekDates.append(dayafter)
    weekDates = [x.strftime("%d/%m/%y") for x in weekDates]
    return weekDates


#dfTurnus=pd.DataFrame(columns=days)
#today=dt.datetime.today()
#today=today.strftime("%d/%m/%y")
#tomorrow=dt.date.today() + dt.timedelta(days=1)
#today=dt.datetime.today()
#thisMonday=today - dt.timedelta(days=today.weekday())
#startingMonday=startingPoint-dt.timedelta(days=startingPoint.weekday())
weeks=[]
weeks.append(weekOutput(refMonday))
weekRow=[]
weekRow.append(weeks[0][0]+" - "+weeks[0][6])
nextMonday=refMonday+dt.timedelta(days=7)

for i in range(numWeeks-1):
    weeks.append(weekOutput(nextMonday))
    weekRow.append(weeks[i+1][0]+" - "+weeks[i+1][6])
    nextMonday=nextMonday+dt.timedelta(days=7)

tuDf.index=weekRow
tuDf["Week Dates"]=weeks
turnus=tuDf.iloc[:,:7]
print(turnus)



