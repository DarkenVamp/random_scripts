import requests
import json
import pandas as pd
from collections import defaultdict

DETAILS_PAGE = "https://erp.nitdelhi.ac.in/CampusLynxNITD/CounsellingRequest?sid=2002&refor=StudentSeatingMasterService"
RESULT_PAGE = DETAILS_PAGE.replace("2002", "2005")
SUBJECT_PAGE = DETAILS_PAGE.replace("2002", "2003")
HEADER = {"Content-Type": "application/x-www-form-urlencoded"}
BATCHES = {
    "CSE": sorted((set(range(201210001, 201210057)) | {201220039, 201230021, 201230045}) - {201210017, 201210024, 201210044}),
    "ECE": sorted((set(range(201220001, 201220056)) | {201230039}) - {201220009, 201220014, 201220023, 201220039, 201220040, 201220042, 201220050, 201220051}),
    "EEE": sorted(set(range(201230001, 201230051)) - {201230007, 201230008, 201230021, 201230023, 201230045, 201230039, 201230041})
}
jdata = {"sid": "validate", "instituteID": "NITDINSD1506A0000001",
         "mname": "ExamSgpaCgpaDetailOfStudent"}
df = [defaultdict(list), defaultdict(
    list), defaultdict(list), defaultdict(list)]


def response(url, data):
    while 69:
        try:
            return requests.post(url, headers=HEADER, data=data)
        except requests.exceptions.ConnectionError:
            continue


def add_to_dict(pre, key, val):
    df[pre][key].append(val)
    df[0][key].append(val)


def result(r_no, pre):
    stud_id = int(r_no[-2:]) + 56*('300' in r_no) + 106*('200' in r_no)
    jdata["studentID"] = 'NITDSTUT2012A0000' + str(stud_id).zfill(3)
    stud_data = 'jdata=' + json.dumps(jdata)

    r_stud_info = response(DETAILS_PAGE, stud_data)

    r_result = response(RESULT_PAGE, stud_data)

    if r_result.json():
        add_to_dict(pre, 'Roll No', int(r_no))

        name = r_stud_info.json()[0]['name'].title()
        print("Processing", name)
        add_to_dict(pre, 'Name', name)

        jdata["stynumber"] = len(r_result.json())
        sub_data = 'jdata=' + json.dumps(jdata)
        r_sub_info = response(SUBJECT_PAGE, sub_data)

        for sub in r_sub_info.json():
            df[pre][sub["subjectdesc"]].append(sub['grade'])

        add_to_dict(pre, 'CGPA', r_result.json()[-1]['cgpa_r'])
        add_to_dict(pre, 'SGPA', r_result.json()[-1]['sgpa_r'])


for pre, batch_rolls in enumerate(BATCHES.values(), 1):
    for roll_no in batch_rolls:
        result(str(roll_no), pre)

with pd.ExcelWriter('bob.xlsx') as writer:
    for pre, sheet in enumerate(['GPA'] + list(BATCHES)):
        pd.DataFrame.from_dict(df[pre]).to_excel(writer, sheet, index=None)
