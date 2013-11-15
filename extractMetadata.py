#!/usr/bin/env python

import os
import csv
from optparse import OptionParser

def findActivityFolder(path, activity):
    for subdir in os.listdir(path):
        fullPath = os.path.join(path, subdir)
        if os.path.isdir(fullPath) and activity in subdir:
            return fullPath
    return None

def parseMeta(path):
    attributeMap = {
            'Activity': 'activity',
            'Gender': 'gender',
            'Generation': 'age',
            'Height(cm)': 'height',
            'Weight(kg)': 'weight',
            'TerminalPosition': 'position',
            'TerminalMount': 'mount',
    }
    data = {
            'id': os.path.basename(path).replace(".meta", ""),
    }
    with open(path) as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) == 2 and parts[0].strip() in attributeMap:
                data[attributeMap[parts[0].strip()]] = parts[1].strip()
    return data

def getDataEntries(path):
    accFiles = {}
    gyroFiles = {}
    metaData = []
    for dirpath, dirnames, filenames in os.walk(path):
        if os.path.basename(dirpath).startswith("person"):
            for filename in filenames:
                fullPath = os.path.join(dirpath, filename)
                if filename.endswith("-acc.csv"):
                    accFiles[filename.replace("-acc.csv", "")] = fullPath
                elif filename.endswith("-gyro.csv"):
                    gyroFiles[filename.replace("-gyro.csv", "")] = fullPath
                elif filename.endswith(".meta"):
                    metaData.append(parseMeta(fullPath))
    return (accFiles, gyroFiles, metaData)

def main():
    parser = OptionParser(usage="usage: %prog [options] directory")

    parser.add_option("-a", "--activity",
            action="store",
            dest="activity",
            default="",
            help="Type of activity to record",)

    parser.add_option("-o", "--output",
            action="store",
            dest="output",
            default="meta.csv",
            help="Type of activity to record",)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("wrong number of arguments")

    # Start parsing
    if options.activity:
        activityFolder = findActivityFolder(args[0], options.activity)
        if activityFolder is None:
            print("Unable to find activity folder for " + options.activity)
            return
    else:
        activityFolder = args[0]

    (accFiles, gyroFiles, metaData) = getDataEntries(activityFolder)
    print len(metaData)

    with open(options.output, 'wb') as csvfile:
        metawriter = csv.writer(csvfile, delimiter=',')
        for entry in metaData:
            record = []
            id = entry['id']
            record.append(id)
            if 'activity' in entry:
                record.append(entry['activity'])
            else:
                record.append('realworld')
            record.append(entry['gender'])
            record.append(entry['age'])
            record.append(entry['height'])
            record.append(entry['weight'])
            record.append(entry['position'])
            if id in accFiles:
                record.append(accFiles[id])
            else:
                record.append("")
            if id in gyroFiles:
                record.append(gyroFiles[id])
            else:
                record.append("")
            metawriter.writerow(record)
    
if __name__ == '__main__':
    main()
