from config import *
from joern.joern_parser import *
from file_utils import *
import pandas as pd
import datetime

import threading
MAX_THREAD = 16

CSV_FILE_PATH_SOURCE = 'sample_data.csv'
CSV_FILE_PATH_OUT = 'sample_info.csv'
out_put_joern = 'joern/output'
MAX_CHANGE_FILE_PER_COMMIT = 2
MAX_OPERATION_CHANGE_FILE_PER_COMMIT = 20


def parser_cpg():
    df = pd.read_csv(CSV_FILE_PATH_OUT, low_memory=False)
    threads = list()
    df = df.sample(frac=1)
    for idx, row in df.iterrows():
        commit_id = row['commit_id']
        file_name = row['filename']
        file_name_old = row['filename_old']
        out_file = join_path(out_put_joern, commit_id)
        print(f'{datetime.datetime.now()} parser: {row["commit_id"]}')
        if row['source_before'] and file_name_old:
            src_before = row['source_before']
            out_filename = file_name+'.before'
            node_p = join_path(out_file, out_filename + ".java.nodes.json")
            if not is_path_exist(node_p):
                t1 = threading.Thread(target=run_joern_text,
                                    args=(src_before, out_file, out_filename))
                t1.start()
                threads.append(t1)
        if row['source_after'] and file_name:
            src_before = row['source_after']
            out_filename = file_name+'.after'
            node_p = join_path(out_file, out_filename + ".java.nodes.json")
            if not is_path_exist(node_p):
                t1 = threading.Thread(target=run_joern_text,
                                    args=(src_before, out_file, out_filename))
                t1.start()
                threads.append(t1)
        if len(threads) > MAX_THREAD:
            for t in threads:
                t.join()
            threads.clear()
    for t in threads:
        t.join()


import re
def preprocess(text):
    text =  re.sub(r"$\d+\W+|\b\d+\b|\W+\d+$", "", text)#remove number
    return re.sub(r'\b[0-9a-f]{40,40}\b','',text)#remove commit hash

if __name__ == '__main__':
    parser_cpg()
