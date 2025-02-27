import csv
import json
from pathlib import Path
import os
from typing import List, Dict
from typedefs import Root, RootT, Category, CategoryT, Appointment, AppointmentT

# Get environment variables
BASE_DIR = Path(os.environ['STUFF_BASE_DIR'])
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

def decode_appointment(csv_appointment: Dict[str, str]) -> Appointment:
    tag: str = csv_appointment['tag']
    title: str = csv_appointment['title']
    date: str = csv_appointment['date']
    start: str = csv_appointment['start']
    end: str = csv_appointment['end']

    appointment = Appointment(
        t=AppointmentT.SUCHMANN_APPOINTMENTS_APPOINTMENT,
        tag=tag,
        title=title,
        date=date,
        start=start,
        end=end,
    )
    return appointment

def read_csv_file(filepath: Path) -> List[Appointment]:
    appointments = []
    if filepath.exists():
        with open(filepath, 'r') as f:
            csv_items = csv.DictReader(f)
            for csv_appointment in csv_items:
                appointments.append(decode_appointment(csv_appointment))
    return appointments

def decode_category(filepath: Path) -> Category:
    name = filepath.stem[3:]
    appointments = read_csv_file(filepath)
    category = Category(
        t=CategoryT.SUCHMANN_APPOINTMENTS_CATEGORY,
        name=name,
        items=appointments,
    )
    return category

def read_csv_folder(folderpath: Path) -> Root:
    categories = []
    csv_files = sorted(folderpath.glob('*.csv'))
    for i in range(len(csv_files)):
        prefix = f'{i:02d}-'
        files_matching_prefix = [f for f in csv_files if f.name.startswith(prefix)]
        if len(files_matching_prefix) != 1: # Do I have to check for None here?
            break

        filepath = files_matching_prefix[0]
        categories.append(decode_category(filepath))

    root = Root(
        t=RootT.SUCHMANN_APPOINTMENTS_ROOT,
        categories=categories,
    )
    return root

def save_json_file(filepath: Path, root: Root):
    with open(filepath, 'w') as f:
        json.dump(root.to_json_data(), f, indent=2)

input = OP_DIR
output = COMPILED_DIR / 'data.json'

root = read_csv_folder(input)
save_json_file(output, root)
