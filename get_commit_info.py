# pass

from config import *
from pydriller import Repository
from joern.joern_parser import *
from file_utils import *
import pandas as pd
import pickle
import threading
MAX_THREAD = 16

CSV_FILE_PATH_SOURCE = 'sample_data.csv'
CSV_FILE_PATH_OUT = 'sample_info.csv'
out_put_joern = 'joern/output'
MAX_CHANGE_FILE_PER_COMMIT = 2
MAX_OPERATION_CHANGE_FILE_PER_COMMIT = 20


def main():
    df = pd.read_csv(CSV_FILE_PATH_SOURCE)
    result = list()
    threads = list()
    for i, group in df.groupby('repo'):
        repo_name = group.head(1)['repo'].values[0]
        repo_dir = join_path(REPOS_DIR, repo_name)
        try:
            lock_dir(repo_dir)
        except BlockingIOError as e:
            continue
        t1 = threading.Thread(target=get_commit_repo,
                              args=(group, repo_name, result))
        t1.start()
        threads.append(t1)
        if len(threads) >= 1:
            for t in threads:
                t.join()
            threads.clear()
    for t in threads:
        t.join()
    dff = pd.DataFrame(result, columns=[
                       "commit_id", 'repo', 'diff', 'filename', 'filename_old', 'delete_lines', 'add_lines', 'source_before', 'source_after'])
    print(dff.shape)
    dff.to_csv(CSV_FILE_PATH_OUT, index=False)


def get_commit_repo(df, repo_name, result):
    repos = list()
    path_save_repo = join_path('data/output', f'commit_info_{repo_name}.pkl')
    print(df.shape)
    if is_path_exist(path_save_repo):
        repos = pickle.load(open(path_save_repo, 'rb'))
        result.extend(repos)
        return
    commits = list(df['commit_id'])
    repos = get_info(commits, repo_name)
    pickle.dump(repos, open(path_save_repo, "wb"))
    result.extend(repos)

def get_info(commit_ids, repo_name):
    repo_dir = join_path(REPOS_DIR, repo_name)
    result = []
    cms = Repository(repo_dir, only_commits=commit_ids,include_refs=True,only_modifications_with_file_types=['.java'],num_workers=MAX_THREAD).traverse_commits()
    for cm in cms:
        commit_id = cm.hash
        if commit_id not in commit_ids:
            continue
        file_change = len(cm.modified_files)
        operation_change = 0
        for mdf in cm.modified_files:
            if not_java_file(mdf.filename):
                file_change -= 1
            diffs = mdf.diff_parsed
            operation_change += (len(diffs['added']) + len(diffs['deleted']))
        if file_change > MAX_CHANGE_FILE_PER_COMMIT or operation_change > MAX_OPERATION_CHANGE_FILE_PER_COMMIT:
            continue
        for mdf in cm.modified_files:
            if not_java_file(mdf.filename):
                continue
            diffs = mdf.diff_parsed
            add_lines = [el[0] for el in diffs['added']]
            delete_lines = [el[0] for el in diffs['deleted']]
            file_name = mdf.new_path.replace('/', '__') if mdf.new_path is not None else mdf.old_path.replace('/', '__')
            file_name_old = mdf.old_path.replace('/', '__') if mdf.old_path is not None else file_name

            if add_lines or delete_lines:
                source_before = mdf.content_before.decode(
                    "utf-8", errors='ignore') if mdf.content_before else None
                source_after = mdf.content.decode(
                    "utf-8", errors='ignore') if mdf.content else None
                result.append([commit_id, repo_name, mdf.diff, file_name, file_name_old, delete_lines,
                            add_lines, source_before, source_after])
    return result


if __name__ == '__main__':
    main()
