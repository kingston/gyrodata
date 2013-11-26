#!/usr/bin/env python

import os
from optparse import OptionParser
import gyrodata

def findActivityFolder(path, activity):
    for subdir in os.listdir(path):
        fullPath = os.path.join(path, subdir)
        if os.path.isdir(fullPath) and activity in subdir:
            return fullPath
    return None

def parseMeta(path, person, activityFolder):
    attributeMap = {
        'Activity': 'activity',
        'Gender': 'gender',
        'Generation': 'age',
        'Height(cm)': 'height',
        'Weight(kg)': 'weight',
        'TerminalPosition': 'position',
        'TerminalMount': 'mount',
        'AttachmentDirection': 'direction',
    }
    data = {
        'id': os.path.basename(path).replace(".meta", ""),
        'person': person,
        'activityFolder': activityFolder,
    }
    with open(path) as f:
        for line in f:
            parts = line.strip().split(':')
            # Weird data in 2011
            if len(parts) == 3:
                parts = [parts[0], parts[2]]
            if len(parts) == 2 and parts[0].strip() in attributeMap:
                data[attributeMap[parts[0].strip()]] = parts[1].strip()
                
    # Generation/weight is not present in 2011 data so set it to 0
    if 'age' not in data:
        data['age'] = 0
    if 'weight' not in data:
        data['weight'] = 0
    
    # check for no mount/direction
    if 'mount' not in data:
        data['mount'] = ""
    if 'direction' not in data:
        data['direction'] = ""
    return data

def formatMetadata(metaData, accFiles, gyroFiles):
    for entry in metaData:
        if 'activity' not in entry:
            entry['activity'] = 'realworld'
        id = entry['id']
        if id in accFiles:
            entry['accfile'] = accFiles[id]
        else:
            entry['accfile'] = ""

        if id in gyroFiles:
            entry['gyrofile'] = gyroFiles[id]
        else:
            entry['gyrofile'] = ""
    return metaData

def getDataEntries(path):
    accFiles = {}
    gyroFiles = {}
    metaData = []
    for dirpath, dirnames, filenames in os.walk(path):
        basename = os.path.basename(dirpath)
        if basename.startswith("person"):
            for filename in filenames:
                fullPath = os.path.join(dirpath, filename)
                if filename.endswith("-acc.csv"):
                    accFiles[filename.replace("-acc.csv", "")] = fullPath
                elif filename.endswith("-gyro.csv"):
                    gyroFiles[filename.replace("-gyro.csv", "")] = fullPath
                elif filename.endswith(".csv"):
                    accFiles[filename.replace(".csv", "")] = fullPath
                elif filename.endswith(".meta"):
                    activityFolder = os.path.basename(os.path.dirname(dirpath))
                    metaData.append(parseMeta(fullPath, basename, activityFolder))
    return formatMetadata(metaData, accFiles, gyroFiles)

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
            help="Output file",)

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

    metaData = getDataEntries(activityFolder)

    gyrodata.writeMetadata(metaData, options.output)

if __name__ == '__main__':
    main()
