import codecs
import gzip
import json
import pandas as pd

from config import *
from file_utils import *

CSV_PATH = 'sample_info.csv'
CSV_FILE_PATH_SOURCE = 'data/message.csv'
CSV_OUTPUT_DEPENDENCY = 'data/data_dependence.csv'
PICKLE_POST = 'pickle'

MAX_INPUT_LENGTH = 400
MAX_THREAD = 64


def load_jsonl_gz(file_name):
    instances = []
    with gzip.GzipFile(file_name, 'r') as f:
        lines = list(f)
    for i, line in enumerate(lines):
        instance = json.loads(line)
        instances.append(instance)
    return instances


def save_to_jsonl_gz(file_name, functions):
    with gzip.GzipFile(file_name, 'wb') as out_file:
        writer = codecs.getwriter('utf-8')
        for entry in functions:
            writer(out_file).write(json.dumps(entry))
            writer(out_file).write('\n')


def convert_data():
    df = pd.read_csv(CSV_OUTPUT_DEPENDENCY, low_memory=False)
    message_dataframe = pd.read_csv(CSV_FILE_PATH_SOURCE, low_memory=False)
    result = list()
    commits = set(df['commit_id'])
    size = len(commits)
    # print(size)
    for index, commit_id in enumerate(commits):
        if index % 1000 == 0:
            # print(index/size)
            pass
        tmp = dict()
        truncation = False
        modiers = df.loc[df['commit_id'] == commit_id]
        message = message_dataframe.loc[message_dataframe['commit_id'] == commit_id]
        tmp['commit_id'] = commit_id
        tmp['message'] = message['commit_msg'].values[0]
        tmp['summary'] = tmp['message'].splitlines()[0]
        tmp['project'] = message['repo'].values[0]
        tmp['language'] = 'java'
        diffs = list()
        tmp_length_diff = 0
        real_length_diff = 0
        diff_uc = list()
        for _, row in modiers.iterrows():
            chunks = list()
            tmp_chuck = dict()
            tmp_chuck['positive_changes'] = row['change_a'].splitlines(
            ) if isinstance(row['change_a'], str) else list()
            tmp_chuck['negative_changes'] = row['change_b'].splitlines(
            ) if isinstance(row['change_b'], str) else list()
            if len(tmp_chuck['positive_changes']) == len(tmp_chuck['negative_changes']) and \
                    len(tmp_chuck['positive_changes']) == 0 and \
                    row['diff_pdg'] and len(row['diff_pdg']) == 0:
                print('IGNORE: ', commit_id)
                continue
            tmp_chuck['chunk_str'] = row['diff_pdg']
            tmp_chuck['chunk_str'] = '\n'.join([line for line in tmp_chuck['chunk_str'].splitlines() if
                                                line.startswith('-') or line.startswith('+')])
            # if _ % 10000 == 0:
            #     print(tmp_chuck['chunk_str'])
            chunk_list = tmp_chuck['chunk_str'].split()
            diff_uc.append([line for line in tmp_chuck['chunk_str'].splitlines() if not (
                line.startswith('-') or line.startswith('+'))])
            real_length_diff += len(chunk_list)
            tmp_length_diff += len(chunk_list)
            chunks.append(tmp_chuck)
            if len(chunk_list) == 0:
                continue
            filename = row['filename'].replace('__', '/')
            filename_old = row['filename_old'].replace('__', '/')
            diffs.append(
                {'negative_changed_file_name': filename_old, 'positive_changed_file_name': filename, 'chunks': chunks})
        if len(diffs) == 0:
            print('IGNORE: ', commit_id)
            continue
        while tmp_length_diff > MAX_INPUT_LENGTH:
            pre_tmp = tmp_length_diff
            for i, diff in enumerate(diffs):
                if tmp_length_diff <= MAX_INPUT_LENGTH:
                    continue
                if len(diff_uc[i]) > 0:
                    rp = diff_uc[i].pop()
                    diff['chunks'][0]['chunk_str'] = diff['chunks'][0]['chunk_str'].replace(
                        rp, '')
                    tmp_length_diff -= len(rp.split())
            if pre_tmp == tmp_length_diff:
                break
            # print(tmp_length_diff)
        tmp['diffs'] = diffs
        tmp['len_input'] = tmp_length_diff
        tmp['real_len'] = real_length_diff
        tmp['truncation'] = truncation
        result.append(tmp)
    # print(len(result))
    save_to_jsonl_gz(CSV_OUTPUT_DEPENDENCY+'.jsonl.gz', result)


if __name__ == '__main__':
    convert_data()
