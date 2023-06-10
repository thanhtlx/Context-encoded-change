from config import JOERN_OUT_PUT
import glob
import os
import re
import shutil
from pathlib import Path


PROJECT_LOCK_FILE_NAME = 'project.lock'


def is_dir_locked(target_dir):
    lock_file_path = join_path(target_dir, PROJECT_LOCK_FILE_NAME)
    return is_path_exist(lock_file_path)


def lock_dir(target_dir):
    if not is_dir_locked(target_dir):
        lock_file_path = join_path(target_dir, PROJECT_LOCK_FILE_NAME)
        touch_file(lock_file_path)
        print(f"Dir [{get_file_name(target_dir)}] has been locked successfully")
    else:
        message = f"Dir [{get_file_name(target_dir)}] had been locked by another process, try again later"
        print(message)
        raise BlockingIOError(message)


def mkdir_if_not_exist(input_dir):
    os.makedirs(input_dir, exist_ok=True)


def get_outer_dir(current_path, step=1):
    current_dir = Path(current_path)
    for _ in range(step):
        current_dir = current_dir.parent
    return current_dir


def find_all_files_by_wildcard(base_dir, file_name, recursive=False):
    return glob.glob(join_path(base_dir, file_name), recursive=recursive)


def find_file_by_wildcard(base_dir, file_name, recursive=False):
    related_files = find_all_files_by_wildcard(base_dir, file_name, recursive)
    if len(related_files):
        return related_files[0]
    return None


def move_file(source, target):
    shutil.move(source, target)


def split_path(file_path):
    return file_path.rsplit(os.sep, 1)


def get_file_name_without_ext(file_path):
    return get_file_name(file_path).rsplit(".", 1)[0]


def get_file_name(file_path):
    return os.path.basename(file_path)


def get_file_name_with_parent(file_path):
    return join_path(*file_path.rsplit(os.sep, 2)[1:])


def join_path(*args, **kwargs):
    return os.path.join(*args, **kwargs)


def is_path_exist(path):
    return os.path.exists(path)


def is_symlink(path):
    return os.path.islink(path)


def get_absolute_path(current_path):
    return os.path.abspath(current_path)


def list_dir(current_dir, full_path=False, sort=False):
    files = list(filter(lambda d: not d.startswith(
        "."), os.listdir(current_dir)))
    if full_path:
        files = [join_path(current_dir, file) for file in files]
    if sort:
        files.sort()
    return files


def remove_dir(directory):
    directory = Path(directory)
    if not directory.is_dir():
        return
    for item in directory.iterdir():
        if item.is_dir():
            remove_dir(item)
        else:
            item.unlink()
    directory.rmdir()


def escape_path(current_path):
    return os.path.normpath(re.sub(r'(?=[()])', r'\\', current_path))


def create_symlink(src, dst):
    if is_path_exist(dst):
        unlink(dst)
    else:
        mkdir_if_not_exist(get_outer_dir(dst))
    os.symlink(src, escape_path(dst))


def unlink(dst):
    try:
        os.unlink(dst)
    except (IsADirectoryError, PermissionError):
        pass


def create_non_hidden_file_symlink(src, dst):
    if is_path_exist(dst):
        unlink(dst)
    mkdir_if_not_exist(dst)
    for file in list_dir(src):
        if file.startswith("."):
            continue
        current_src = join_path(src, file)
        current_dst = join_path(dst, file)
        create_symlink(current_src, current_dst)


def remove_file(file_path):
    os.remove(file_path)


def write_file(file_path, content, skip_if_existed=False):
    if skip_if_existed and is_path_exist(file_path):
        return file_path
    else:
        mkdir_if_not_exist(get_outer_dir(file_path))

    with open(file_path, "w", encoding="utf-8", errors='ignore') as out_f:
        out_f.write(content)
    return file_path


def copy_file(src, dst):
    if is_path_exist(dst):
        remove_dir(dst)
    shutil.copyfile(src, dst)


def copy_dir(src, dst, delete_existing_dir=True):
    if delete_existing_dir and is_path_exist(dst):
        remove_dir(dst)
    shutil.copytree(src, dst)


def touch_file(file_path):
    Path(file_path).touch()
# v1 without compare attribute code
# v2 have compare attribute code
def get_ctg_path(commit, file_name):
    base_path = join_path(JOERN_OUT_PUT, commit)
    ctg_nodes_path = join_path(base_path, f"{file_name}.ctgv2.nodes.json")
    ctg_edges_path = join_path(base_path, f"{file_name}.ctgv2.edges.json")
    return ctg_nodes_path, ctg_edges_path

def get_ctg_sliced_path(commit, file_name):
    base_path = join_path(JOERN_OUT_PUT, commit)
    ctg_nodes_path = join_path(base_path, f"{file_name}.ctg_slicedv2.nodes.json")
    ctg_edges_path = join_path(base_path, f"{file_name}.ctg_slicedv2.edges.json")
    return ctg_nodes_path, ctg_edges_path


def get_source_path(commit, file_name):
    base_path = join_path(JOERN_OUT_PUT, commit)
    source_after = join_path(base_path, f"{file_name}.after.java")
    source_before = join_path(base_path, f"{file_name}.before.java")
    return source_before, source_after

def get_diff_path(commit, file_name):
    base_path = join_path(JOERN_OUT_PUT, commit)
    diff_path = join_path(base_path, f"{file_name}.diff.html")
    return diff_path

def get_cpg_after(commit, file_name):
    base_path = join_path(JOERN_OUT_PUT, commit)
    a_nodes_path = join_path(base_path, f'{file_name}.after.java.nodes.json')
    a_edges_path = join_path(base_path, f'{file_name}.after.java.edges.json')
    return a_nodes_path, a_edges_path

def get_cpg_before(commit, file_name):
    base_path = join_path(JOERN_OUT_PUT, commit)
    b_nodes_path = join_path(base_path, f'{file_name}.before.java.nodes.json')
    b_edges_path = join_path(base_path, f'{file_name}.before.java.edges.json')
    return b_nodes_path, b_edges_path