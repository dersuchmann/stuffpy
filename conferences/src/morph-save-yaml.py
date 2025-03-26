import csv
import json
import yaml
from pathlib import Path
import os
from typing import List, Dict, Any
from typedefs import Root, RootT
import typedefs
import re
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


def decode_room(yaml_room: Dict[str, Any]):
    venue: str = yaml_room['venue']
    name: str = yaml_room['name']
    i = typedefs.RoomI(venue=venue, name=name)
    
    room = typedefs.Room(
        t=typedefs.RoomT.SUCHMANN_CONFERENCES_ROOM,
        i=i,
        h=stuff_hash(i),
    )
    return room

def decode_person(yaml_person: Dict[str, Any]):
    first_name: str = yaml_person['first_name']
    last_name: str = yaml_person['last_name']
    disambiguator: str = yaml_person['disambiguator']
    i = typedefs.PersonI(first_name=first_name, last_name=last_name, disambiguator=disambiguator)
    
    person = typedefs.Person(
        t=typedefs.PersonT.SUCHMANN_CONFERENCES_PERSON,
        i=i,
        h=stuff_hash(i),
    )
    return person

def decode_event(yaml_event: Dict[str, Any]):
    session_h: str = yaml_event['sessionH']
    title: str = yaml_event['title']
    i = typedefs.EventI(session_h=session_h, title=title)
    
    order: int = yaml_event['order']
    person_hs: list[str] = yaml_event['personHs']
    url: str = yaml_event['url']
    
    event = typedefs.Event(
        t=typedefs.EventT.SUCHMANN_CONFERENCES_EVENT,
        i=i,
        h=stuff_hash(i),
        order=order,
        person_hs=person_hs,
        url=url,
    )
    return event

def decode_session(yaml_session: Dict[str, Any]):
    name: str = yaml_session['name']
    i = typedefs.SessionI(name=name)
    
    room_h: str = yaml_session['roomH']
    date: str = yaml_session['date']
    start: str = yaml_session['start']
    end: str = yaml_session['end']
    events: list[typedefs.Event] = []
    for yaml_event in yaml_session['events']:
        events.append(decode_event(yaml_event))
    
    session = typedefs.Session(
        t=typedefs.SessionT.SUCHMANN_CONFERENCES_SESSION,
        i=i,
        h=stuff_hash(i),
        room_h=room_h,
        date=date,
        start=start,
        end=end,
        events=events,
    )
    return session

def decode_sv_data(yaml_sv_data: Dict[str, Any]):
    am_i_sv: str = yaml_sv_data['am_i_sv']
    if am_i_sv == "no":
        sv_data = typedefs.SvDataNo(am_i_sv=am_i_sv)
    else: # if am_i_sv == "yes":
        my_sv_jobs: list[typedefs.SvJob] = []
        for yaml_sv_job in yaml_sv_data['my_sv_jobs']:
            my_sv_jobs.append(decode_sv_job(yaml_sv_job))
        sv_data = typedefs.SvDataYes(am_i_sv=am_i_sv, my_sv_jobs=my_sv_jobs)
    return sv_data

def decode_sv_job(yaml_sv_job: Dict[str, Any]):
    type_: str = yaml_sv_job['type']
    if type_ == "session":
        session_h: str = yaml_sv_job['sessionH']
        note: str = yaml_sv_job['note']
        sv_job = typedefs.SvJobSession(type=type_, session_h=session_h, note=note)
    elif type_ == "registration":
        date: str = yaml_sv_job['date']
        start: str = yaml_sv_job['start']
        end: str = yaml_sv_job['end']
        sv_job = typedefs.SvJobRegistration(type=type_, date=date, start=start, end=end)
    else: # if type_ == "quick_response":
        date: str = yaml_sv_job['date']
        start: str = yaml_sv_job['start']
        end: str = yaml_sv_job['end']
        sv_job = typedefs.SvJobQuickResponse(type=type_, date=date, start=start, end=end)
    return sv_job

def decode_conference(yaml_conference: Dict[str, Any]):
    name: str = yaml_conference['name']
    year: int = yaml_conference['year']
    i = typedefs.ConferenceI(name, year)
    
    location: str = yaml_conference['location']
    rooms: list[typedefs.Room] = []
    for yaml_room in yaml_conference['rooms']:
        rooms.append(decode_room(yaml_room))
    persons: list[typedefs.Person] = []
    for yaml_person in yaml_conference['persons']:
        persons.append(decode_person(yaml_person))
    sessions: list[typedefs.Session] = []
    for yaml_session in yaml_conference['sessions']:
        sessions.append(decode_session(yaml_session))
    sv_data = decode_sv_data(yaml_conference['sv_data'])
    
    conference = typedefs.Conference(
        t=typedefs.ConferenceT.SUCHMANN_CONFERENCES_CONFERENCE,
        i=i,
        h=stuff_hash(i),
        location=location,
        rooms=rooms,
        persons=persons,
        sessions=sessions,
        sv_data=sv_data,
    )
    return conference

def decode_root(yaml_root: Dict[str, Any]):
    conferences: List[typedefs.Conference] = []
    for yaml_conference in (yaml_root['conferences'] or []):
        conferences.append(decode_conference(yaml_conference))
    
    root = Root(
        t=RootT.SUCHMANN_CONFERENCES_ROOT,
        conferences=conferences,
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


