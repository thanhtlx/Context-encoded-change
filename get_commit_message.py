import pickle
import threading

import pandas as pd

from file_utils import *
from utils import subprocess_cmd

ROOT_DIR_REPO = '../repo'
NUM_THREAD = 32


def clean_msg(text):
    if not isinstance(text, str):
        return text
    text = text.strip().splitlines()
    ll = ['-Url:', '-id:', '-by:', 'Cc:', 'CC:',
          '-Id:', ' URL:', 'Cr-Commit-Position:', '-Url:',
          'Author:', 'Reviewers:']
    while True:
        tmp = len(text)
        for st in ll:
            text = list(filter(lambda line: st not in line, text))
        if tmp == len(text):
            break
    return '\n'.join(text)


def process_data(commit, repo_name, commit_msg0, result):
    commit_msg = commit_msg0.strip()
    if 'Rollback of' in commit_msg or 'Merged commit' in commit_msg or 'Squashed commit' in commit_msg or 'Merge branch' in commit_msg:
        return
    commit_msg = clean_msg(commit_msg.strip())
    len_msg = len(commit_msg.split(' '))
    if len(commit_msg) > 0 and len_msg  > 20 and len_msg < 200 and len(commit_msg.splitlines()) < 10:
        result.append([commit, repo_name, commit_msg0])


def get_commit_msg(repo_dir):
    repo_name = get_file_name(repo_dir)
    out_put_file_dir = f'data/output/{repo_name}.csv'
    if is_path_exist(out_put_file_dir):
        return
    cmd = f"cd {repo_dir} && git --no-pager log"
    rs = subprocess_cmd(cmd)
    result = list()
    index = 0
    commit_msg = ''
    commit = ''
    if rs[1]:
        print(rs[1])
        return
    cms = list()
    threads = list()
    for line in rs[0].splitlines():
        index += 1
        if line.startswith("commit"):
            cms.append([commit, commit_msg])
            t1 = threading.Thread(target=process_data,
                                  args=(commit, repo_name, commit_msg, result))
            t1.start()
            threads.append(t1)
            if len(threads) > NUM_THREAD:
                for t in threads:
                    t.join()
                threads.clear()
            commit_msg = ''
            commit = line[7:]
            assert len(commit) == 40
        if line.startswith(' '):
            line = line.strip()
            if len(line) > 0:
                commit_msg += ('\n' + line)
    for t in threads:
        t.join()
    process_data(commit, repo_name, commit_msg, result)
    df = pd.DataFrame(result, columns=['commit_id', 'repo', 'commit_msg'])
    print(df.shape)
    pickle.dump(cms, open(out_put_file_dir+'.pkl', "wb"))
    df.to_csv(out_put_file_dir, index=False)


def main():
    for repo_name in list_dir(ROOT_DIR_REPO)[::-1]:
        repo_dir = join_path(ROOT_DIR_REPO, repo_name)
        print(f'procesing {repo_name}')
        get_commit_msg(repo_dir)


if __name__ == '__main__':
    main()
