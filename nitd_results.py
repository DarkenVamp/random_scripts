import requests
from urllib3.exceptions import InsecureRequestWarning
import json
import pandas as pd
from multiprocessing import Pool
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DETAILS_PAGE = "https://erp.nitdelhi.ac.in/CampusLynxNITD/CounsellingRequest?sid=2002&refor=StudentSeatingMasterService"
RESULT_PAGE = DETAILS_PAGE.replace("2002", "2005")
SUBJECT_PAGE = DETAILS_PAGE.replace("2002", "2003")
HEADER = {"Content-Type": "application/x-www-form-urlencoded"}
BRANCHES = {
    "CSE": list(range(201210001, 201210057)) + [201220039, 201230021, 201230045],
    "ECE": sorted((set(range(201220001, 201220056)) | {201230039}) - {201220039}),
    "EEE": sorted(set(range(201230001, 201230051)) - {201230021, 201230039, 201230045})
}
jdata = {"sid": "validate", "instituteID": "NITDINSD1506A0000001",
         "mname": "ExamSgpaCgpaDetailOfStudent"}


def response(url: str, data: str) -> requests.Response:
    while 69:
        try:
            return requests.post(url, headers=HEADER, data=data, verify=False)
        except requests.exceptions.ConnectionError:
            continue


def result(r_no: str) -> dict:
    stud_id = int(r_no[-2:]) + 56*('300' in r_no) + 106*('200' in r_no)
    jdata["studentID"] = 'NITDSTUT2012A0000' + str(stud_id).zfill(3)
    stud_data = 'jdata=' + json.dumps(jdata)

    r_stud_info = response(DETAILS_PAGE, stud_data)
    r_result = response(RESULT_PAGE, stud_data)

    if r := r_result.json():
        if not r[-1]['sgpa_r']:
            return {}

        name = r_stud_info.json()[0]['name'].title()
        print("Processing", name)
        result_info = {'Roll No': int(r_no), 'Name': name}

        jdata["stynumber"] = len(r)
        sub_data = 'jdata=' + json.dumps(jdata)
        r_sub_info = response(SUBJECT_PAGE, sub_data)

        for sub in r_sub_info.json():
            result_info[sub["subjectdesc"]] = sub['grade']

        result_info['CGPA'], result_info["SGPA"] = r[-1]['cgpa_r'], r[-1]['sgpa_r']
        return result_info


if __name__ == '__main__':
    df, gpa = [], []

    with Pool() as pool:
        for branch_rolls in BRANCHES.values():
            cur_branch = []

            for res_info in pool.imap(result, map(str, branch_rolls)):
                if not res_info:
                    continue
                gpa_data = list(res_info.items())
                gpa_data = dict(gpa_data[:2] + gpa_data[-2:])
                gpa.append(gpa_data)
                cur_branch.append(res_info)
            df.append(pd.DataFrame(cur_branch))

    df.insert(0, pd.DataFrame(gpa))

    # Remove backlog/dropouts by checking if they do not have the first subject of first roll number
    for i in range(4):
        df[i] = df[i].dropna(subset=[df[i].columns[2]]).dropna(axis=1)

    with pd.ExcelWriter('bob.xlsx') as writer:
        for i, sheet in enumerate(['GPA'] + list(BRANCHES)):
            df[i].to_excel(writer, sheet, index=None)
