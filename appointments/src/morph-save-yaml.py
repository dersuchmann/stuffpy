import yaml
import json
from pathlib import Path
import os
from typing import List, Dict
from typedefs import Root, RootT, Category, CategoryT, Appointment, AppointmentT

# Get environment variables
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

def decode_appointment(yaml_appointment: Dict[str, str]) -> Appointment:
    tag: str = yaml_appointment['tag']
    title: str = yaml_appointment['title']
    date: str = yaml_appointment['date']
    start: str = yaml_appointment['start']
    end: str = yaml_appointment['end']

    appointment = Appointment(
        t=AppointmentT.SUCHMANN_APPOINTMENTS_APPOINTMENT,
        tag=tag,
        title=title,
        date=date,
        start=start,
        end=end,
    )
    return appointment

def decode_category(yaml_category: Dict[str, str]):
    name: str = yaml_category['name']

    items: List[Appointment] = []
    for yaml_appointment in (yaml_category['items'] or []):
        items.append(decode_appointment(yaml_appointment))

    category = Category(
        t=CategoryT.SUCHMANN_APPOINTMENTS_CATEGORY,
        name=name,
        items=items,
    )
    return category

def decode_root(yaml_root: List[Dict[str, str]]):
    categories: List[Category] = []
    for yaml_category in (yaml_root['categories'] or []):
        categories.append(decode_category(yaml_category))

    root = Root(
        t=RootT.SUCHMANN_APPOINTMENTS_ROOT,
        categories=categories,
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


