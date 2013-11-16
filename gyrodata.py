# Library for accessing gyro data
import os, csv

def getAttributeList():
    return ['activity', 'gender', 'age', 'height', 'weight', 'position', 'activityFolder', 'person', 'accfile', 'gyrofile']

def writeMetadata(data, path):
    with open(path, 'wb') as csvfile:
        metawriter = csv.writer(csvfile, delimiter=',')
        for entry in data:
            record = []
            for attr in getAttributeList():
                record.append(entry[attr])
            metawriter.writerow(record)

def readMetadata(path):
    data = []    
    with open(path, 'r') as csvfile:
        metareader = csv.reader(csvfile)
        for row in metareader:
            data.append(dict(zip(getAttributeList(), row)))
    return data

def readCsvData(path):
    with open(path, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        return list(csvreader)

def writeCsvData(data, path):
    with open(path, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerows(data)
