use convert_case::{Case, Casing};
use indexmap::IndexMap;
use polars_core::prelude::{DataFrame, NamedFrom, Series};
use serde::Deserialize;
use std::collections::HashMap;

#[derive(Deserialize)]
struct StudentDetail {
    name: String,
}

#[derive(Deserialize)]
struct StudentResult {
    sgpa_r: f32,
    cgpa_r: f32,
}

#[derive(Deserialize)]
struct SubjectResult {
    subjectdesc: String,
    grade: String,
}

const DETAILS_PAGE: &str = "https://erp.nitdelhi.ac.in/CampusLynxNITD/CounsellingRequest?sid=2002&refor=StudentSeatingMasterService";
const RESULT_PAGE: &str = "https://erp.nitdelhi.ac.in/CampusLynxNITD/CounsellingRequest?sid=2005&refor=StudentSeatingMasterService";
const SUBJECT_PAGE: &str = "https://erp.nitdelhi.ac.in/CampusLynxNITD/CounsellingRequest?sid=2003&refor=StudentSeatingMasterService";

fn student_id(r_no: String) -> String {
    let mut stud_id = r_no[r_no.len() - 2..].parse::<u8>().unwrap();

    if r_no.contains("300") {
        stud_id += 56;
    } else if r_no.contains("200") {
        stud_id += 106;
    }

    format!("{:0width$}", stud_id, width = 3)
}

pub fn prepare_branch_data() -> HashMap<String, Vec<i32>> {
    let mut branches: HashMap<String, Vec<i32>> = HashMap::from([
        ("CSE".to_string(), (201210001..201210057).collect()),
        ("ECE".to_string(), (201220001..201220056).collect()),
        ("EEE".to_string(), (201230001..201230051).collect()),
    ]);

    let cse = branches.get_mut("CSE").unwrap();
    cse.append(&mut vec![201220039, 201230021, 201230045]);

    let ece = branches.get_mut("ECE").unwrap();
    ece.retain(|&r_no| r_no != 201220039);
    ece.push(201230039);

    let eee = branches.get_mut("EEE").unwrap();
    eee.retain(|&r_no| r_no != 201230021 && r_no != 201230039 && r_no != 201230045);

    branches
}

pub async fn result(r_no: String, mut jdata: HashMap<String, String>) -> IndexMap<String, String> {
    let stud_id = "NITDSTUT2012A0000".to_string() + student_id(r_no.clone()).as_str();
    jdata.insert("studentID".to_string(), stud_id);

    let mut stud_data = String::from("jdata=") + serde_json::to_string(&jdata).unwrap().as_str();
    let mut result_info = IndexMap::new();

    let client = reqwest::Client::builder()
        .danger_accept_invalid_certs(true)
        .build()
        .unwrap();

    let r_stud_info = client
        .post(DETAILS_PAGE)
        .header("Content-Type", "application/x-www-form-urlencoded")
        .body(stud_data.clone())
        .send()
        .await
        .unwrap();

    let r_result = client
        .post(RESULT_PAGE)
        .header("Content-Type", "application/x-www-form-urlencoded")
        .body(stud_data.clone())
        .send()
        .await
        .unwrap();

    if let Ok(result) = r_result.json::<Vec<StudentResult>>().await {
        if result.last().is_none() || result.last().unwrap().sgpa_r == 0.0 {
            return result_info;
        }

        let name = r_stud_info.json::<Vec<StudentDetail>>().await.unwrap()[0]
            .name
            .to_case(Case::Title);
        println!("Processing {}", name);

        result_info.insert("Roll No".to_string(), r_no);
        result_info.insert("Name".to_string(), name);

        jdata.insert("stynumber".to_string(), result.len().to_string());
        stud_data = String::from("jdata=") + serde_json::to_string(&jdata).unwrap().as_str();

        let r_sub_info = client
            .post(SUBJECT_PAGE)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(stud_data.clone())
            .send()
            .await
            .unwrap();

        for sub in r_sub_info.json::<Vec<SubjectResult>>().await.unwrap() {
            result_info.insert(sub.subjectdesc, sub.grade);
        }

        let latest_sem = result.last().unwrap();
        result_info.insert("CGPA".to_string(), latest_sem.cgpa_r.to_string());
        result_info.insert("SGPA".to_string(), latest_sem.sgpa_r.to_string());
    }

    result_info
}

fn parse_gpa(df: &Vec<DataFrame>) -> DataFrame {
    let column_names = ["Roll No", "Name", "CGPA", "SGPA"];
    let mut gpa = DataFrame::empty();

    for branch_data in df {
        let branch_gpa = branch_data.select(column_names).unwrap();
        gpa.vstack_mut(&branch_gpa).unwrap();
    }

    gpa.align_chunks();
    gpa
}

pub fn convert_to_df(result_info: Vec<(String, Vec<IndexMap<String, String>>)>) -> Vec<DataFrame> {
    let mut df = Vec::new();

    for (_branch_name, branch_data) in result_info {
        let mut series_vec = Vec::new();

        for key in branch_data[0].keys() {
            let values = Series::new(
                key,
                &branch_data
                    .iter()
                    .map(|mp| mp.get(key).cloned())
                    .collect::<Vec<_>>(),
            );

            series_vec.push(values);
        }

        df.push(DataFrame::new(series_vec).unwrap());
    }

    df.insert(0, parse_gpa(&df));

    for i in 1..df.len() {
        df[i] = df[i].drop_nulls::<String>(None).unwrap();
    }

    df
}
