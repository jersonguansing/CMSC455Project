import time
import os
import re
import gc
from datetime import datetime
import numpy as np
from numpy.linalg import solve
from numpy.linalg import linalg
try:
	from collections import Counter
except ImportError:
	# gl is still running python 2.6.6
	from Counters import *

try:
    input = raw_input
except NameError:
    raw_input = input

df, priorities, districts, columnHeaders = [], [], [], []

def readFile(fileName):
    global priorities
    global districts
    global columnHeaders
    X = []
    headers = True
    count = 0
    with open(fileName, "r") as f:
        for line in f:
            line = line.replace("\n","").split(",")
            if headers == True:
                if count == 0:
                    priorities = line
                elif count == 1:
                    districts = line
                else:
                    columnHeaders = line
                    headers = False
                count += 1
            else:
                line = [ float(i) for i in line ]
                X.append(line)
    return X

def dayOfYear(callDate):
    daysInMonth = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    year, month, day = int(callDate[6:]), int(callDate[:2]), int(callDate[3:5])
    returnValue = day + sum(daysInMonth[0:month])
    returnValue += (1 if year % 4 == 0 and month > 2 else 0)
    if year % 4 == 0 and month > 2:
        returnValue += 1
    del year; del month; del day
    return returnValue

def getErrors(x, y, coefficients):
    # get the computer y value with the given coefficients
    #y_computed = [ sum([ (i**j)*coefficients[j] for j in range(len(coefficients))]) for i in x ]
    y_computed = [ sum(i[j]*coefficients[j+1] for j in range(len(i)))+coefficients[0] for i in x]
    #print(y_computed)
    # absolute value of actual value - computer value
    absError = [ abs(y[i] - y_computed[i]) for i in range(len(y)) ]
    maxError = max(absError)
    avgError = sum(absError) / len(absError)
    #  sqrt(sum_over_set(absolute_error^2)/number_in_set)
    rmsError = (sum(map(lambda a: a**2, absError))/len(absError))**(1/2.0)
    del y_computed
    return maxError, avgError, rmsError

def getCoefficient(x, y, constantTerm = True):
    # Given numeric data points, find an equation that approximates the data with a least square fit
    # where x is not one dimensional
    # add one to one to include the constant term to make the fit
    # | SUM( 1* 1)  SUM( 1*X1)  SUM( 1*X2)  SUM( 1*X3) |   | Y0 |   | SUM( 1*Y) |
    # | SUM(X1* 1)  SUM(X1*X1)  SUM(X1*X2)  SUM(X1*X3) |   | a  |   | SUM(X1*Y) |
    # | SUM(X2* 1)  SUM(X2*X1)  SUM(X2*X2)  SUM(X2*X3) | x | b  | = | SUM(X2*Y) |
    # | SUM(X3* 1)  SUM(X3*X1)  SUM(X3*X2)  SUM(X3*X3) |   | c  |   | SUM(X3*Y) |
    n = len(x[0])
    if constantTerm == True:
        n += 1
    A = [ [0.0 for i in range(n) ] for j in range(n) ]
    Y = [ 0.0 for i in range(n) ]
    for i in range(n):
        if constantTerm == True:
            Y[i] = sum(map(lambda a,b: a[i - 1]*b if i > 0 else b, x, y))
            for j in range(n):
                A[i][j] = sum(map(lambda a: (a[i - 1] if i > 0 else 1)*(a[j - 1] if j > 0 else 1), x))
        else:
            Y[i] = sum(map(lambda a,b: a[i]*b, x, y))
            for j in range(n):
                A[i][j] = sum(map(lambda a: a[i]*a[j], x))
    #return solve(A, Y)
    return linalg.lstsq(A, Y)
try:
	print("Importing the data file as a list...")
	df = readFile("./Cleaned_DataFile.csv")
	print("Total entries: " + str(len(df)))
except IOError:
	print("The file Cleaned_DataFile.csv not found.")
	quit()

print("Getting user criteria")
getDate = ""
whichColumns = []
getMonth, getDay, getYear, getDayOfYear, getHour, getHourMax, getWeekDay, getPriority, getDistrict = -1, -1, -1,-1, -1, -1, -1, -1, -1
weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
daysInMonth = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
while True:
    getDate, getMonth, getDay, getYear, getDayOfYear, getWeekDay = "", -1, -1, -1, -1, -1
    getDate = raw_input("Enter required date (mm/dd/yyyy) starting from 2014 : ")
    if re.compile(r"^[0-9]{2}/[0-9]{2}/[0-9]{4}$").match(getDate):
        getMonth, getDay, getYear = int(getDate[0:2]), int(getDate[3:5]), int(getDate[6:])
        if getMonth >= 1 and getMonth <= 12 and getYear >= 2014:
            if getDay >= 1 and getDay <= daysInMonth[getMonth]:
                getWeekDay = datetime.strptime(getDate, '%m/%d/%Y').weekday()
                getDayOfYear = dayOfYear(getDate)
                whichColumns += ["month","day","dayOfYear"]
                break
        print("Please enter a valid date.")
    else:
        print("Please enter a valid date.")

while True:
    displayMsg = "Enter optional day of week\n"
    if getWeekDay>= 0:
        displayMsg += "Hitting enter sets it to current day of the week: " + weekdays[getWeekDay] + ")\n"
        displayMsg += "Enter 'No' or 'N' to skip this criteria\n"
    else:
        displayMsg += "Hit enter to skip this"
    print(displayMsg)
    temp1 = raw_input(str(weekdays) + ": ").upper().strip().replace(" ", "")
    if temp1 != "":
        success = False
        if temp1 == "NO" or temp1 == "N":
            getWeekDay = -1
            break
        for i in weekdays:
            if temp1 == i:
                success = True
                break
        if success == True:
            break
        print("Please enter a value from the listed options.")
    else:
        break
if getWeekDay >= 0:
    whichColumns += ["dayOfWeek"]
while True:
    getHour, getHourMax = -1, -1
    print("Enter optional call hour (ex. 1) or call hour range (ex. 1-7)\n")
    temp1 = raw_input("Call hour (0-23) or hit enter to skip: ")
    if temp1 != "":
        if re.compile(r"^[0-9]{1,2}-[0-9]{1,2}$").match(temp1):
            ind1 = temp1.index("-")
            getHour = int(temp1[0:ind1])
            getHourMax = int(temp1[ind1+1:])
            if (getHour < getHourMax) and (getHour >= 0 and getHour <= 23) and (getHourMax >= 0 and getHourMax <= 23):
                whichColumns += ["callHour"]
                break
        if re.compile(r"^[0-9]{1,2}$").match(temp1):
            getHour = int(temp1)
            if getHour >= 0 and getHour <= 23:
                whichColumns += ["callHour"]
                break
        print("Please enter a value between 0-23.")
    else:
        break

while True:
    getDistrict = -1
    print("Enter optional district (enter to skip)")
    temp1 = raw_input(str(districts) + ": ").upper().strip().replace(" ", "")
    if temp1 != "":
        success = False
        for i in districts:
            if temp1 == i:
                success = True
                getDistrict = districts.index(temp1)
                whichColumns += ["district"]
                break
        if success == True:
            break
        print("Please enter a value from the listed districts")
    else:
        break

displayText = ""
for i in range(len(priorities)):
    displayText += " " + priorities[i] + "=" + str(i) + " "
while True:
    getPriority = -1
    print("Enter optional call priority (enter to skip)")
    temp1 = raw_input(displayText + ": ")
    if temp1 != "":
        if re.compile(r"^[0-9]{1,2}$").match(temp1):
            getPriority = int(temp1)
            if getPriority >= 0 and getPriority < len(priorities):
                whichColumns += ["priority"]
                break
            else:
                getPriority = -1
        print("Enter a numeric value corresponding to the priority.")
    else:
        break
## decided not to include longitude and latitude for user criteria
## because for general use cases, the user will not be interested in
## the call volume for a specific GPS coordinate (long, lat)
## it will be district-based if they want call volume by location
## however, the data is still available and the code can be easily adapted
## to include those towards an N degree polynomial regression

print("Using the columns: " + str(whichColumns))
# subset the data based on user criteria
print("Generating subset data based on user criteria")
subset = []
for i in df:
    line = []
    if getMonth >= 0:
        line.append(i[0])
    if getDay >= 0:
        line.append(i[1])
    if getYear >= 0:
        line.append(i[2])
    if getDayOfYear >= 0:
        line.append(i[3])
    if getWeekDay >= 0 and getWeekDay <= 6:
        line.append(i[6])
    if getHour >= 0:
        line.append(i[4])
    if getPriority >= 0 and getPriority <= len(priorities):
        line.append(i[7])
    if getDistrict >= 0:
        line.append(i[8])
    subset.append(line)
subset = tuple(tuple(i) for i in subset)

print("Aggregating y value (call volume) based on user criteria")
time3 = time.clock()
c = Counter(subset)
yValues = []
uniques = []
for i, j in c.items():
    uniques.append(i)
    yValues.append(j)
time4 = time.clock()
print("Time it took to generate y dataset: " + str(time4 - time3))

print("Performing " + str(len(uniques[0]) ) + " degree polynomial regression")
time3 = time.clock()
coefficients = getCoefficient(uniques, yValues)[0]
errors = getErrors(uniques, yValues, coefficients)
time4 = time.clock()
print("Time it took to solve the matrix: " + str(time4 - time3))


print("Polynomial coefficients: x0 + x1 + ... + xn")
print(coefficients)
print("Max Error, Avg Error, RMS Error")
print(errors)

estimate = 0.0
n = len(uniques[0])
rmin, rmax = 0, 1
if getHour >= 0:
    rmin, rmax = getHour, getHour + 1
if getHourMax >= 0:
    rmax = getHourMax

for i in range(rmin, rmax):
    count = 1
    estimate += coefficients[0]
    if getMonth >= 0:
        estimate += getMonth * coefficients[count]
        count += 1
    if getDay >= 0:
        estimate += getDay * coefficients[count]
        count += 1
    if getYear >= 0:
        estimate += getYear * coefficients[count]
        count += 1
    if getDayOfYear >= 0:
        estimate += getDayOfYear * coefficients[count]
        count += 1
    if getWeekDay >= 0 and getWeekDay <= 6:
        estimate += getWeekDay * coefficients[count]
        count += 1
    if getHour >= 0:
        # for getHour to getHourMax
        estimate += i * coefficients[count]
        count += 1
    if getPriority >= 0 and getPriority <= len(priorities):
        estimate += getPriority * coefficients[count]
        count += 1
    if getDistrict >= 0:
        estimate += getDistrict * coefficients[count]
        count += 1

print("Estimated call volume: " + str(estimate))

