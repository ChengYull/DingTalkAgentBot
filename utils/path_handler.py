import os

def get_project_root():
    cur_path = os.path.abspath(__file__)
    cur_dir = os.path.dirname(cur_path)
    project_root = os.path.dirname(cur_dir)
    return project_root

def get_abs_path(relative_path: str):
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)