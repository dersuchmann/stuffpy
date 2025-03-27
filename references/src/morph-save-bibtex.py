import bibtexparser
import bibtexparser.model
import json
from pathlib import Path
import os
from typing import List, Dict, Any
from typedefs import Root, RootT
import typedefs
import fnvhash

def stuff_hash(i: Any):
    temp = hex(fnvhash.fnv1a_32(bytes(repr(i), encoding="utf-8")))[2:].zfill(8)
    return temp[:4] + '_' + temp[4:]



# Get environment variables
BASE_DIR = Path(os.environ['STUFF_BASE_DIR'])
SOURCE_DIR = Path(os.environ['STUFF_SOURCE_DIR'])
REPO_DIR = Path(os.environ['STUFF_REPO_DIR'])
COMPILED_DIR = Path(os.environ['STUFF_COMPILED_DIR'])
OP_DIR = Path(os.environ['STUFF_OP_DIR'])

def decode_field(bibtex_field: bibtexparser.model.Field):
    key: str = bibtex_field.key
    value: str = bibtex_field.value
    
    field = typedefs.EntryField(
        key=key,
        value=value,
    )
    return field

def decode_entry(bibtex_entry: bibtexparser.model.Entry):
    key: str = bibtex_entry.key
    i = typedefs.EntryI(key=key)
    h = stuff_hash(i)

    entry_type: str = bibtex_entry.entry_type
    fields: list[typedefs.EntryField] = []
    for bibtex_field in bibtex_entry.fields:
        fields.append(decode_field(bibtex_field))

    entry = typedefs.Entry(
        t=typedefs.EntryT.SUCHMANN_REFERENCES_ENTRY,
        i=i,
        h=h,
        entry_type=entry_type,
        fields=fields,
    )
    return entry

def decode_root(bibtex_root: bibtexparser.Library):
    entries: List[typedefs.Entry] = []
    for bibtex_entry in bibtex_root.entries:
        entries.append(decode_entry(bibtex_entry))
    
    root = Root(
        t=RootT.SUCHMANN_REFERENCES_ROOT,
        entries=entries,
    )
    return root

def read_bibtex_file(filepath: Path) -> Root:
    if filepath.exists():
        bibtex_root = bibtexparser.parse_file(filepath)
        root = decode_root(bibtex_root)
    return root

def write_json_file(filepath: Path, root: Root):
    with open(filepath, 'w') as f:
        json.dump(root.to_json_data(), f, indent=2)

input: Path = OP_DIR / 'allrefs_2025.bib'
output: Path = COMPILED_DIR / 'data.json'

root = read_bibtex_file(input)
write_json_file(output, root)


