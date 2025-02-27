import yaml
from yaml.representer import Representer
from yaml.dumper import Dumper
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

class CustomDumper(Dumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)
        if len(self.indents) in [2, 4]:
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

def encode_appointment(appointment: Appointment) -> Dict:
    return {
        'tag': appointment.tag,
        'title': appointment.title,
        'date': appointment.date,
        'start': appointment.start,
        'end': appointment.end,
    }

def encode_category(category: Category) -> Dict:
    return {
        'name': category.name,
        'items': None if len(category.items) == 0 else [encode_appointment(appointment) for appointment in category.items],
    }

def encode_root(root: Root) -> Dict:
    return {
        'categories': None if len(root.categories) == 0 else [encode_category(category) for category in root.categories],
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
