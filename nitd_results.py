import requests
import json
from time import sleep

LOGIN_PAGE = "https://erp.nitdelhi.ac.in/CampusLynxNITD/CounsellingRequest?sid=validate&refor=StudentOnlineDetailService"
RESULT_PAGE = LOGIN_PAGE.replace("validate", "2002").replace(
    "OnlineDetail", "SeatingMaster")
headers = {"Content-Type": "application/x-www-form-urlencoded"}


def result(r_no):
    jdata = {"sid": "validate",
             "instituteID": "NITDINSD1506A0000001", "studentrollno": r_no}
    login_data = 'jdata=' + json.dumps(jdata)
    stud_id = requests.post(LOGIN_PAGE, headers=headers,
                            data=login_data).text

    jdata.update(
        {"sid": "2005", "mname": "ExamSgpaCgpaDetailOfStudent", "studentID": stud_id})
    stud_data = 'jdata=' + json.dumps(jdata)
    r_stud_info = requests.post(RESULT_PAGE,
                                headers=headers, data=stud_data)

    r_result = requests.post(RESULT_PAGE.replace('2002', '2005'),
                             headers=headers, data=stud_data)

    jdata.update({"sid": "2003", "mname": "studentGrade"})

    if r_result.json():
        print("Roll No:", r_no)

        name = r_stud_info.json()[0]['name'].title()
        print("Name:", name)

        for sem, res in enumerate(r_result.json(), 1):
            jdata.update({"stynumber": sem})
            sub_data = 'jdata=' + json.dumps(jdata)
            r_sub_info = requests.post(RESULT_PAGE.replace('2002', '2003'),
                                       headers=headers, data=sub_data)

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
