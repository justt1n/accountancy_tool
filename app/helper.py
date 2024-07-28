import requests
import json
import csv

import requests


def sendGetRequest(url):
    custom_headers = {
        'User-Agent': 'hihi',
    }

    response = requests.get(url, headers=custom_headers)

    if response.status_code == 200:
        print('Success!')
        return response.text
    else:
        print('Error!')
        print(response.status_code)
    return None


def fetchApi(url):
    custom_headers = {
        'User-Agent': 'hihi',
    }
    response = requests.get(url, headers=custom_headers)

    if response.status_code == 200:
        json_data = response.json()
        print("Fetch API successful!")
        return json_data
    else:
        print(f"Failed to retrieve data from the API. Status code: {response.status_code}")
    return None

def dumpJson(data, filename):
    with open(filename, "w") as outfile:
        outfile.write(data)


def loadJson(filename):
    with open(filename, "r") as infile:
        data = infile.read()
    return data


def writeCSV(filename, data, fieldnames):
    with open('app/storage/' + filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            row = {field: item[field] for field in fieldnames if field in item}
            writer.writerow(row)


def readCSV(filename, fieldnames):
    data = []
    with open('app/storage/' + filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = {field: row[field] for field in fieldnames if field in row}
            data.append(item)
    return data
