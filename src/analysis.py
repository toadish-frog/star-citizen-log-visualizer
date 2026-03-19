from typing import List
from datetime import datetime, timedelta
import re

from log_parser import DeathEvent, SessionMetadata

def calculate_total_deaths(death_events: List[DeathEvent]) -> int:
    """Calculates the total number of deaths."""
    return len(death_events)

def get_log_session_duration(log_content: str) -> str:
    """
    Calculates the total session duration by finding the first and last
    timestamps in the log file.
    """
    # This regex is broad to catch any timestamp at the start of a line.
    timestamp_regex = re.compile(r"^<(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)>")
    
    lines = log_content.splitlines()
    
    first_timestamp = None
    last_timestamp = None
    
    # Find the first valid timestamp
    for line in lines:
        match = timestamp_regex.match(line)
        if match:
            first_timestamp = match.group(1)
            break
            
    # Find the last valid timestamp
    for line in reversed(lines):
        match = timestamp_regex.match(line)
        if match:
            last_timestamp = match.group(1)
            break

    if not first_timestamp or not last_timestamp:
        return "00:00:00"
        
    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    
    try:
        start_dt = datetime.strptime(first_timestamp, time_format)
        end_dt = datetime.strptime(last_timestamp, time_format)
        
        duration = end_dt - start_dt
        
        # Format into HH:MM:SS
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    except (ValueError, TypeError):
        return "00:00:00"
