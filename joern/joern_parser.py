# from config import BASE_DIR
from utils import *
from file_utils import *
import logging
import os 
BASE_DIR = os. getcwd()

CURRENT_DIR = get_outer_dir(__file__)
JOERN_SCRIPT_PATH = join_path(CURRENT_DIR, "scripts", "get_func_graph_parse.scala")

logger = logging.getLogger(__name__)

def run_joern_text(function_text, output_dir, fileName = ""):
    node_p = join_path(output_dir, fileName + ".java.nodes.json")
    edge_p = join_path(output_dir, fileName + ".java.edges.json")
    if is_path_exist(node_p) and is_path_exist(edge_p):
        print("Already parsed")
        return
    if function_text is None or isinstance(function_text,float):
        write_file(node_p,"[]")
        write_file(edge_p,"[]")
        return
    mkdir_if_not_exist(output_dir)
    cm_id = output_dir.rsplit("/")[-1]
    workspace_name = cm_id + str(get_current_timestamp())+fileName
    tmp_file = join_path(output_dir,fileName+".java")
    if not is_path_exist(tmp_file):
        with open(tmp_file, "w+") as f:
            f.write(function_text)
    mkdir_if_not_exist(output_dir)
    logger.info(f"Exporting joern graph [{output_dir}]")
    # tmp_file = '/home/thanh/Desktop/nckh/dataset/test.java'
    params = f"filepath={tmp_file},outputDir={output_dir},workspaceName={workspace_name}"
    command = f"joern --script {JOERN_SCRIPT_PATH} --params='{params}'"
    logger.debug(command)
    try:
        subprocess_cmd_joern(command)
    except RuntimeError as e:
        print("Joern parser err: ",output_dir)
        write_file(node_p,"[]")
        write_file(edge_p,"[]")
        return
    workspace_dir = join_path(BASE_DIR, "workspace", workspace_name)
    try:
        remove_dir(workspace_dir)
    except Exception as e:
        logger.warning(f"Failed to remove workspace {workspace_dir}")
    return output_dir