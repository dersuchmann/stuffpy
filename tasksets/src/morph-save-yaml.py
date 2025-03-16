import yaml
import json
from pathlib import Path
import os
from typing import List, Dict
from typedefs import Root, RootT, Taskset, TasksetT, Task, TaskT

# Get environment variables
BASE_DIR = Path(os.environ['STUFF_BASE_DIR'])
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

def decode_task(yaml_task: Dict[str, str]) -> Task:
    name: str = yaml_task['name']
    
    task = Task(
        t=TaskT.SUCHMANN_TASKSETS_TASK,
        name=name,
    )
    return task

def decode_taskset(yaml_taskset: Dict[str, str]):
    name: str = yaml_taskset['name']
    
    completed_tasks: List[Task] = []
    for yaml_completed_task in (yaml_taskset['completed_tasks'] or []):
        completed_tasks.append(decode_task(yaml_completed_task))
    
    tasks: List[Task] = []
    for yaml_task in (yaml_taskset['tasks'] or []):
        tasks.append(decode_task(yaml_task))
    
    taskset = Taskset(
        t=TasksetT.SUCHMANN_TASKSETS_TASKSET,
        name=name,
        completed_tasks=completed_tasks,
        tasks=tasks,
    )
    return taskset

def decode_root(yaml_root: List[Dict[str, str]]):
    tasksets: List[Taskset] = []
    for yaml_taskset in (yaml_root['tasksets'] or []):
        tasksets.append(decode_taskset(yaml_taskset))
    
    root = Root(
        t=RootT.SUCHMANN_TASKSETS_ROOT,
        tasksets=tasksets,
    )
    return root

def read_yaml_file(filepath: Path) -> Root:
    if filepath.exists():
        with open(filepath, 'r') as f:
            yaml_root: List[Dict[str, str]] = yaml.safe_load(f) or []
            root = decode_root(yaml_root)
    return root

def write_json_file(filepath: Path, root: Root):
    with open(filepath, 'w') as f:
        json.dump(root.to_json_data(), f, indent=2)

input: Path = OP_DIR / 'data.yaml'
output: Path = COMPILED_DIR / 'data.json'

root = read_yaml_file(input)
write_json_file(output, root)


