import time
from datetime import datetime
import os
import numpy as np

df = np.array([])

def cleanData(whichIndex):
    global df
    totalRecords = len(df)
    removelist = np.array([])
    for i in np.unique(df[:,whichIndex]):
        sublist = np.where(df[:,whichIndex] == i)[0]
        # check if the sublist is an outlier -- less than 0.1%
        if len(sublist) < float(totalRecords) / 1000.0:
            removelist = np.concatenate((removelist, sublist), axis=0)
    df = np.delete(df, list(removelist), 0)

def dayOfYear(callDate):
    daysInMonth = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    year, month, day = int(callDate[6:]), int(callDate[:2]), int(callDate[3:5])
    returnValue = day + sum(daysInMonth[0:month])
    returnValue += (1 if year % 4 == 0 and month > 2 else 0)
    if year % 4 == 0 and month > 2:
        returnValue += 1
    del year; del month; del day
    return returnValue

def readFile(fileName):
    X = []
    with open(fileName, "r") as f:
        for line in f:
            line = line.split(",")
            # remove columns that are too varied from initial tests with jupyter notebook
            # these are unique callNumber, incident location, and description
            line.pop(4); line.pop(4); line.pop(3)
            # split the calldatetime into calldate and calltime
            format24hr = line[0][11:13]
            if line[0][20:].upper() == "PM":
                if format24hr == "12":
                    format24hr = "00"
                else:
                    format24hr = str(int(format24hr) + 12)
            if format24hr == "24":
                print(format24hr)
            format24hr += ":" + line[0][14:16]
            # calltime
            line.insert(0, format24hr)
            # calldate
            line.insert(0, line[1][0:10])
            # remove calldatetime
            line.pop(2)
            if len(line) == 6:
                # make sure every entry have a priority value
                if line[2] == "" or line[2] is None:
                    line[2] = "Unknown"
                # clean longitude and latitude values
                line[4] = line[4].replace("\"(", "")
                if line[4] == "":
                    line[4] = "0.0"
                line[4] = round(float(line[4]), 3)
                line[5] = line[5].replace(")\"", "").replace("\n", "")
                if line[5] == "":
                    line[5] = "0.0"
                line[5] = round(float(line[5]), 3)
                line.insert(2, datetime.strptime(line[0], '%m/%d/%Y').weekday())
                line.insert(0, line[0][0:2])
                line.insert(1, line[1][3:5])
                line.insert(2, line[2][6:10])
                line.insert(3, dayOfYear(line[3]))
                line.pop(4)
                line.insert(4, line[4][0:2])
                line.insert(5, line[5][3:5])
                line.pop(6)
                X.append(line)
    return np.array(X)

# Dataset from Open Baltimore
fileName = "./Calls_for_Service.csv"
print("Looking for the data file " + fileName)
# download the dataset if the file is not found or less than 1mB
if not os.path.isfile(fileName) or os.path.getsize(fileName) < 10E5:
    print("Downloading the data file " + fileName + "...")
    time3 = time.clock()
    webAddress = "http://data.baltimorecity.gov/api/views/xviu-ezkt/rows.csv?accessType=DOWNLOAD"
    os.system("curl " + webAddress + " > " + fileName)
    time4 = time.clock()
    print("Download complete!")
    print("Time it took to download dataset: " + str(time4 - time3))
else:
    print("File size: " + str(os.path.getsize(fileName)) + " bytes")

print("Importing the data file as a list...")
df = readFile(fileName)
print("Total entries before removing outliers: " + str(len(df)))

print("Removing outliers (less than 0.1%) of the total entries...")
for i in range(len(df[0])):
    # clean the data of outliers based on the column
    cleanData(i)
print("Total entries after removing outliers: " + str(len(df)))

priorities = list(np.unique(df[:,7]))
districts = list(np.unique(df[:,8]))
for i in df:
    i[7] = priorities.index(i[7])
    i[8] = districts.index(i[8])

print("Writing cleaned data to file...")
f = open("Cleaned_DataFile.csv", "w")
f.write(','.join(priorities) + "\n")
f.write(','.join(districts) + "\n")
f.write("month,day,year,dayOfYear,callHour,callMin,dayOfWeek,priority,district,longitude,latitude\n")
for i in df:
    f.write(','.join(i) + "\n")
f.close()
print("Writing complete!")
