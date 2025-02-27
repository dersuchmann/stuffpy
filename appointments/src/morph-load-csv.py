import csv
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

def encode_appointment(appointment: Appointment) -> Dict:
    return {
        'tag': appointment.tag,
        'title': appointment.title,
        'date': appointment.date,
        'start': appointment.start,
        'end': appointment.end,
    }

def write_csv_file(filepath: Path, appointments: List[Appointment]):
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['tag', 'title', 'date', 'start', 'end'])
        writer.writeheader()
        for appointment in appointments:
            writer.writerow(encode_appointment(appointment))

def write_csv_folder(folderpath: Path, root: Root):
    for i, category in enumerate(root.categories):
        filepath = folderpath / f'{i:02d}-{category.name}.csv'
        write_csv_file(filepath, category.items)

def read_json_file(filepath: Path) -> Root:
    with open(filepath, 'r') as f:
        return Root.from_json_data(json.load(f))

input = COMPILED_DIR / 'data.json'
output = OP_DIR

root = read_json_file(input)
write_csv_folder(output, root)
