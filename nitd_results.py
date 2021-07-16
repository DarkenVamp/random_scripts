import requests
import json
from time import sleep

DETAILS_PAGE = "https://erp.nitdelhi.ac.in/CampusLynxNITD/CounsellingRequest?sid=2002&refor=StudentSeatingMasterService"
RESULT_PAGE = DETAILS_PAGE.replace("2002", "2005")
SUBJECT_PAGE = DETAILS_PAGE.replace("2002", "2003")
headers = {"Content-Type": "application/x-www-form-urlencoded"}
jdata = {"sid": "validate", "instituteID": "NITDINSD1506A0000001",
         "mname": "ExamSgpaCgpaDetailOfStudent"}


def result(r_no):
    stud_id = int(r_no[-2:]) + 56*('300' in r_no) + 106*('200' in r_no)
    jdata["studentID"] = 'NITDSTUT2012A0000' + str(stud_id).zfill(3)
    stud_data = 'jdata=' + json.dumps(jdata)

    r_stud_info = requests.post(DETAILS_PAGE, headers=headers, data=stud_data)

    r_result = requests.post(RESULT_PAGE, headers=headers, data=stud_data)

    if r_result.json():
        print("Roll No:", r_no)

        name = r_stud_info.json()[0]['name'].title()
        print("Name:", name)

        for sem, res in enumerate(r_result.json(), 1):
            jdata["stynumber"] = sem
            sub_data = 'jdata=' + json.dumps(jdata)
            r_sub_info = requests.post(
                SUBJECT_PAGE, headers=headers, data=sub_data)

            print("Sem", sem, "Results :-")
            for sub in r_sub_info.json():
                print(sub["subjectcode"], '-', sub['grade'])

            print("CGPA :", res['cgpa_r'], '\n')


batches = {"CSE": 57, "ECE": 56, "EEE": 51}
for pre, (batch, strength) in enumerate(batches.items(), 1):
    print(batch, ":\n")
    for i in range(1, strength):
        roll_no = '2012' + str(pre) + '00' + str(i).zfill(2)
        try:
            result(roll_no)
        except requests.exceptions.ConnectionError:
            sleep(5)
            result(roll_no)
