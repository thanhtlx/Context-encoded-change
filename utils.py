import subprocess
from config import TIME_OUT
from subprocess import STDOUT, check_output
import logging
from collections import defaultdict


def get_logger(name):
    return logging.getLogger(name)

def get_node_in_line(line, nodes):
    result = list()
    for node in nodes:
        if node['lineNumber'] == line:
            result.append(node['id'])
    return result


def get_dependece_with_node(change_nodes_id, nodes, edges,LEVEL_SLICE=1):
    edges_only = ['CDG', 'REACHING_DEF']
    edges = [e for e in edges if e[2] in edges_only]
    set_node_id_dependence = set(list(change_nodes_id))
    slicing = [[n,n,['CDG','REACHING_DEF'],0] for n in set_node_id_dependence]    
    # 1 layer 
    map_0_e = defaultdict(lambda:list())
    map_1_e = defaultdict(lambda: list())
    for e in edges:
        map_0_e[e[0]].append(e)
        map_1_e[e[1]].append(e)
    while len(slicing) > 0:
        slice_element = slicing.pop(0)
        if slice_element[3] >= LEVEL_SLICE:#check sliced level
            continue
        if slice_element[0]:
            for ee in map_0_e[slice_element[0]]:#lay edge id source = slice_element[0]
                if ee[2] in slice_element[2]: # lay edge co co canh slice_element[2]
                    if ee[1] in set_node_id_dependence: # check chua travesal
                        continue
                    bb = [ee[1],None,[ee[2]],slice_element[3]+1] # add e: slice_element[0]== ee[0] -> ee[1] = ee2[0] -> ee2[1]
                    set_node_id_dependence.add(ee[1])
                    slicing.append(bb)
                    
        if slice_element[1]:
            for ee in map_1_e[slice_element[1]]:
                if ee[2] in slice_element[2]:#check edges
                    bb = [None,ee[0],[ee[2]],slice_element[3]+1] # add e: ee2[0] -> ee2[1] == ee[0] -> ee[1] = sliced_element[1]
                    slicing.append(bb)
                    set_node_id_dependence.add(ee[0])
    node_dependence = [n for n in nodes if n['id'] in set_node_id_dependence]
    return [n['lineNumber'] for n in node_dependence if 'lineNumber' in n]


def get_dependece_with_node_old(change_nodes_id, nodes, edges,LEVEL_SLICE=1):
    edges_only = ['CDG', 'REACHING_DEF']
    edges = [e for e in edges if e[2] in edges_only]
    set_node_id_dependence = set()
    for e in edges:
        if e[1] in change_nodes_id:
            set_node_id_dependence.add(e[0])
        if e[0] in change_nodes_id:
            set_node_id_dependence.add(e[1])
    node_dependence = [n for n in nodes if n['id'] in set_node_id_dependence]
    return [n['lineNumber'] for n in node_dependence if 'lineNumber' in n]


def get_dependece_line(change_lines, nodes, edges):
    # nodes = [node for node in nodes if 'lineNumber' in node]
    result = set()
    nodes_in_lines = list()
    # get all node in change line 
    for line in change_lines:
        nodes_in_lines.extend(get_node_in_line(line, nodes))
        
    nodes_in_lines = set(nodes_in_lines)
    lines = get_dependece_with_node(nodes_in_lines, nodes, edges)
    result.update(lines)
    for line in change_lines:
        if line in result:
            result.remove(line)
    # depen not line 
    return result


def subprocess_cmd(command: str):
    """Run command line process.

    Example:
    subprocess_cmd('echo a; echo b', verbose=1)
    """
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    try:
        stout, stderr = process.communicate()
    except:
        raise RuntimeError("Error when run command: timeout!!")
    finally:
        pass
    return stout.decode(errors='ignore'), stderr.decode(errors='ignore')


def subprocess_cmd_joern(command: str):
    """Run command line process.

    Example:
    subprocess_cmd('echo a; echo b', verbose=1)
    """
    try:
        output = check_output(command, stderr=STDOUT, timeout=TIME_OUT, shell=True)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Error when run command: timeout!!")

    return 


import time
def get_current_timestamp():
    return round(time.time())

def not_java_file(file_name):
    ext = file_name.rsplit('.', 1)
    if len(ext) < 2 or (len(ext) > 1 and ext[1] not in ['java']):
        return True
    return False