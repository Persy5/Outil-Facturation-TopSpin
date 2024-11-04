from typing import List
from models.audita.audita_data import AuditaData
from datetime import datetime
import re
import os
import pytz

TARGET = "started at"

def interpret_audita_files(audita_file_paths: List[str]):
    audita_data_list: List[AuditaData] = []
    for audita_file_path in audita_file_paths:
        audita_data = open_audita_file_and_interpret(audita_file_path)
        audita_data_list.append(audita_data)
    return audita_data_list

def open_audita_file_and_interpret(audita_file_path: str) -> AuditaData:
    start_time: datetime = get_start_time(audita_file_path)
    end_time: datetime = get_end_time(audita_file_path)
    return AuditaData(start_time, end_time, audita_file_path)

def get_start_time(audita_file_path: str) -> datetime:
    audita_start_line: str = ""
    with open(audita_file_path, "r") as f:
        for line in f:
            line: str
            if TARGET in line:
                audita_start_line = line
    date_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} -\d{4})', audita_start_line)

    if date_match:
        date_str: str = date_match.group(1)
        date_obj: datetime = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f %z')
    
    if not date_obj:
        raise ValueError("Start Date not found.")
    
    return date_obj

def get_end_time(audita_file_path: str) -> datetime:
    timestamp = os.path.getmtime(audita_file_path)
    uqam_timezone = pytz.timezone('America/New_York')
    last_modified_date = datetime.fromtimestamp(timestamp, uqam_timezone)
    return last_modified_date