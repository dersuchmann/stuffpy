import yaml
from yaml.representer import Representer
from yaml.dumper import Dumper
import json
from pathlib import Path
import os
from typing import List, Dict
from typedefs import Root, RootT, Taskset, TasksetT, Task, TaskT

# Get environment variables
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

class CustomDumper(Dumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)
        if len(self.indents) == 2:
            super().write_line_break()

# https://stackoverflow.com/a/67524482
class BlankNone(Representer):
    """Print None as blank when used as context manager"""
    def represent_none(self, *_):
        return self.represent_scalar(u'tag:yaml.org,2002:null', u'')
    def __enter__(self):
        self.prior = Dumper.yaml_representers[type(None)]
        yaml.add_representer(type(None), self.represent_none)
    def __exit__(self, exc_type, exc_val, exc_tb):
        Dumper.yaml_representers[type(None)] = self.prior

def encode_task(task: Task) -> Dict:
    return {
        'name': task.name,
    }

def encode_taskset(taskset: Taskset) -> Dict:
    return {
        'name': taskset.name,
        'completed_tasks': None if len(taskset.completed_tasks) == 0 else [encode_task(task) for task in taskset.completed_tasks],
        'tasks': None if len(taskset.tasks) == 0 else [encode_task(task) for task in taskset.tasks],
    }

def encode_root(root: Root) -> Dict:
    return {
        'tasksets': None if len(root.tasksets) == 0 else [encode_taskset(taskset) for taskset in root.tasksets],
    }

def write_yaml_file(filepath, root):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with BlankNone(), open(filepath, 'w') as f:
        yaml_root = encode_root(root)
        yaml.dump(yaml_root, f, Dumper=CustomDumper, sort_keys=False, indent=2, allow_unicode=True)

def read_json_file(filepath: Path) -> Root:
    with open(filepath, 'r') as f:
        return Root.from_json_data(json.load(f))

input: Path = COMPILED_DIR / 'data.json'
output: Path = OP_DIR / 'data.yaml'

root = read_json_file(input)
write_yaml_file(output, root)
