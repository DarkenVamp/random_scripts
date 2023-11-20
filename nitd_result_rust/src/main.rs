use nitd_result::{convert_to_df, prepare_branch_data, result};
use polars_io::{csv::CsvWriter, SerWriter};
use std::collections::HashMap;
use std::fs::File;

#[tokio::main]
async fn main() {
    let jdata = HashMap::from([
        ("sid".to_string(), "validate".to_string()),
        (
            "instituteID".to_string(),
            "NITDINSD1506A0000001".to_string(),
        ),
        (
            "mname".to_string(),
            "ExamSgpaCgpaDetailOfStudent".to_string(),
        ),
    ]);

    let branches = prepare_branch_data();
    let mut branch_threads = Vec::with_capacity(3);

    for (branch, rolls) in branches.clone() {
        let jdata_clone = jdata.clone();

        let branch_thread = tokio::spawn(async move {
            let mut cur_branch = Vec::with_capacity(rolls.len());
            for r_no in rolls {
                let res_info = result(r_no.to_string(), jdata_clone.to_owned()).await;

                if res_info.is_empty() {
                    continue;
                }
                cur_branch.push(res_info);
            }
            (branch, cur_branch)
        });

        branch_threads.push(branch_thread);
    }

    let mut result_info = Vec::with_capacity(branch_threads.len());

    for thread in branch_threads {
        if let Ok(branch_data) = thread.await {
            result_info.push(branch_data);
        }
    }

    result_info.sort_unstable_by_key(|b| b.0.to_owned());
    let mut df_vec = convert_to_df(result_info);

    for (branch, dataframe) in [String::from("GPA")]
        .iter()
        .chain(branches.keys())
        .zip(df_vec.iter_mut())
    {
        let mut file = File::create(format!("{}.csv", branch)).unwrap();
        CsvWriter::new(&mut file)
            .include_header(true)
            .with_separator(b',')
            .finish(dataframe)
            .unwrap();
    }
}
