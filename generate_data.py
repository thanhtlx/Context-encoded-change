import pickle
import json
import pandas as pd
from config import *
from file_utils import *
from utils import get_dependece_line
import multiprocessing as mp

CSV_PATH = 'sample_info.csv'
CSV_FILE_PATH_SOURCE = 'data/message.csv'
CSV_OUTPUT_DEPENDENCY = 'data/data_dependence.csv'
PICKLE_POST = 'pickle'


MAX_INPUT_LENGTH = 400
MAX_THREAD = 64


def parser_dependence_code_change():
    result = list()
    df = pd.read_csv(CSV_PATH, low_memory=False)
    size = df.shape[0]
    mode = True
    for index, row in df.iterrows():
        if index % 1000 == 0:  # type: ignore
            print(index/size)  # type: ignore
            pass
        if mode:
            res = parser_program_dependence(row, list())
            if res is None:
                continue
            result.append(res)
        else:
            pool.apply_async(parser_program_dependence, args=(row, result))
    pool.close()
    pool.join()
    df = pd.DataFrame(result)
    df.to_csv(CSV_OUTPUT_DEPENDENCY, index=False)


def get_program_dependence(nodes_path, edges_path, change_lines):
    maps = dict()
    invert = dict()
    change_lines = json.loads(change_lines) if change_lines else list()
    faild_get_result = [list(), list(), maps, invert]
    if not change_lines:
        return faild_get_result
    if not is_path_exist(nodes_path) or not is_path_exist(edges_path):
        return faild_get_result
    with open(nodes_path) as f:
        nodes = json.load(f)
        nodes = [n for n in nodes if 'lineNumber' in n]
    with open(edges_path) as f:
        edges = json.load(f)
    if len(nodes) == 10 or len(edges) < 20:
        return faild_get_result
    lines_dependence = set()
    lines_code = list()
    c_lines = list()
    # get all change lines
    for line in change_lines:
        if len(lines_code) > 0 and line not in lines_code:
            continue
        c_lines.append(line)

    lines_dependence.update(get_dependece_line(change_lines, nodes, edges))
    lines = sorted(list(lines_dependence))

    for idx, line in enumerate(lines):
        tmp = 0
        for c_line in c_lines:
            if c_line < line:
                tmp += 1
        maps[line] = line - tmp
        invert[line-tmp] = line
    return [lines, c_lines, maps, invert]


def parser_program_dependence(row, result):
    commit_id = row['commit_id']
    ff = f'data/gencpg/{commit_id}.{PICKLE_POST}'
    if is_path_exist(ff):
        return pickle.load(open(ff, 'rb'))
    file_name = row['filename']
    after_nodes_path, after_edges_path = get_cpg_after(commit_id, file_name)
    after_pdg = get_program_dependence(
        after_nodes_path, after_edges_path, row['add_lines'])
    before_nodes_path, before_edges_path = get_cpg_before(commit_id, file_name)
    before_pdg = get_program_dependence(
        before_nodes_path, before_edges_path, row['delete_lines'])
    if len(after_pdg[1]) == 0 and len(before_pdg[1]) == 0:
        return
    source_before = row['source_before'].splitlines() if isinstance(
        row['source_before'], str) else list()
    source_after = row['source_after'].splitlines() if isinstance(
        row['source_after'], str) else list()
    source_after.insert(0, '')
    source_before.insert(0, '')
    un_change_a = [after_pdg[2][line] for line in after_pdg[0]]
    un_change_b = [before_pdg[2][line] for line in before_pdg[0]]
    un_change = set(un_change_a+un_change_b)
    un_change = sorted(list(un_change))
    diff_pdg = list()
    change_a = list()
    change_b = list()

    for line in un_change:
        # dung while thi dung hon la if
        while len(before_pdg[1]) and line in before_pdg[3]:
            if before_pdg[3][line] < before_pdg[1][0]:
                break
            ll = before_pdg[1][0]
            diff_pdg.append('-' + source_before[ll])
            change_b.append(source_before[ll].strip())
            before_pdg[1].pop(0)

        while len(after_pdg[1]) and line in after_pdg[3]:
            if after_pdg[3][line] < after_pdg[1][0]:
                break
            ll = after_pdg[1][0]
            diff_pdg.append('+' + source_after[ll])
            change_a.append(source_after[ll].strip())
            after_pdg[1].pop(0)
        if line in before_pdg[3]:
            ll = before_pdg[3][line]
            diff_pdg.append(source_before[ll])
        elif line in after_pdg[3]:
            ll = after_pdg[3][line]
            diff_pdg.append(source_after[ll])
        else:
            print('Parser pdg error:', row['commit_id'])

    while len(before_pdg[1]) > 0 or len(after_pdg[1]) > 0:
        l_b = before_pdg[1][0] if len(before_pdg[1]) else 0
        l_a = after_pdg[1][0] if len(after_pdg[1]) else 0
        if l_b > l_a:
            ll = before_pdg[1][0]
            diff_pdg.append('-' + source_before[ll])
            change_b.append(source_before[ll].strip())
            before_pdg[1].pop(0)
        else:
            ll = after_pdg[1][0]
            diff_pdg.append('+' + source_after[ll])
            change_a.append(source_after[ll].strip())
            after_pdg[1].pop(0)

    row['diff_pdg'] = '\n'.join(diff_pdg)
    row['change_a'] = '\n'.join(change_a)
    row['change_b'] = '\n'.join(change_b)
    result.append(row)
    with open(ff, 'wb') as handle:
        pickle.dump(row, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return row


pool = mp.Pool(mp.cpu_count())
if __name__ == '__main__':
    parser_dependence_code_change()
