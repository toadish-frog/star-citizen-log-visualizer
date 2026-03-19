import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

# --- Dataclasses for storing parsed data ---

@dataclass
class GameMetadata:
    build: Optional[str] = None
    file_version: Optional[str] = None
    product_version: Optional[str] = None
    branch: Optional[str] = None
    executable: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class TimeMetadata:
    log_start: Optional[str] = None
    build_time: Optional[str] = None
    local_time: Optional[str] = None
    login_time: Optional[str] = None

@dataclass
class ProcessorInfo:
    name: Optional[str] = None
    count: Optional[int] = None

@dataclass
class MemoryInfo:
    total_physical_mb: Optional[int] = None
    available_physical_mb: Optional[int] = None
    usage_percent: Optional[int] = None

@dataclass
class DisplayInfo:
    graphics_card: Optional[str] = None
    display_mode: Optional[str] = None
    resolution: Optional[str] = None

@dataclass
class DeviceMetadata:
    processor: ProcessorInfo = field(default_factory=ProcessorInfo)
    memory: MemoryInfo = field(default_factory=MemoryInfo)
    display: DisplayInfo = field(default_factory=DisplayInfo)
    language: Optional[str] = None

@dataclass
class NetworkMetadata:
    hostname: Optional[str] = None

@dataclass
class UserMetadata:
    system_login: Optional[str] = None
    actor_name: Optional[str] = None

@dataclass
class SessionMetadata:
    game: GameMetadata = field(default_factory=GameMetadata)
    time: TimeMetadata = field(default_factory=TimeMetadata)
    device: DeviceMetadata = field(default_factory=DeviceMetadata)
    network: NetworkMetadata = field(default_factory=NetworkMetadata)
    user: UserMetadata = field(default_factory=UserMetadata)

@dataclass
class DeathEvent:
    timestamp: str
    death_type: str
    player_name: Optional[str] = None
    ship_brand: Optional[str] = None
    ship_make: Optional[str] = None
    approx_loc: Optional[str] = None

@dataclass
class TravelEvent:
    start_time: str
    end_time: str
    duration_seconds: float
    ship: str
    destination: str
    start_location: Optional[str] = None
    fuel_used: Optional[float] = None


# --- Regex patterns for all parsing ---

PATTERNS = {
    # Session Metadata
    'game_build': re.compile(r'build_version\[(\d+)\]'),
    'file_version': re.compile(r'FileVersion: ([\d\.]+)'),
    'product_version': re.compile(r'ProductVersion: ([\d\.]+)'),
    'branch': re.compile(r'Branch: ([\w\d\.-]+)'),
    'executable': re.compile(r'Executable: (.*)'),
    'session_id': re.compile(r"@session:\s+'([^']*)'"),
    'log_start': re.compile(r'Log started on (.*)'),
    'build_time': re.compile(r'Built on (.*)'),
    'local_time': re.compile(r'Local time is (.*)'),
    'login_time': re.compile(r'nickname="([^"]+)" playerGEID=\d+ uptime_secs='),
    'cpu_name': re.compile(r'Host CPU: (.*)'),
    'cpu_count': re.compile(r'Logical CPU Count: (\d+)'),
    'memory': re.compile(r'(\d+)MB physical memory installed, (\d+)MB available, (\d+) percent of memory in use'),
    'gpu': re.compile(r'-\s(NVIDIA|AMD|Intel)\s(.*)\s\(vendor'),
    'display_mode': re.compile(r'Current display mode is (.*)'),
    'resolution': re.compile(r'Change resolution: (.*)'),
    'language': re.compile(r'System language: (.*)'),
    'hostname': re.compile(r'network hostname: (.*)'),
    'system_login': re.compile(r"Successfully activated profile 'default' for user '([^']*)'"),
    'actor_name': re.compile(r'name\s([a-zA-Z0-9_]+)\s-\sstate'),
    
    # Death Events
    'death_in_ship': re.compile(r"<(?P<timestamp>.*?)>.*Actor '(?P<player_name>.*?)' \[\d+\] ejected from zone '(?P<ship>.*?)' \[\d+\] to zone '(?P<location>.*?)'"),
    'death_on_foot': re.compile(r'<(?P<timestamp>.*?)> \[Notice\] <UpdateNotificationItem> Notification "Incapacitated:.*?" \[(?P<id>\d+)\], Action: (Next|RemoveIgnore)'),

    # Travel Events
    'travel_select_dest': re.compile(r"<(?P<timestamp>.*?)>.*\| (?P<ship_id>.*?)\[\d+\]\|.*Player has selected point (?P<destination>\S+) as their destination"),
    'travel_calc_route': re.compile(r"<(?P<timestamp>.*?)>.*\| (?P<ship_id>.*?)\[\d+\]\|.*Projected Start Location is (?P<start_loc>\S+) for route to destination (?P<destination>\S+)"),
    'travel_fuel_est': re.compile(r"<(?P<timestamp>.*?)>.*\| (?P<ship_id>.*?)\[\d+\]\|.*Successfully calculated route to (?P<destination>\S+) fuel estimate (?P<fuel>\d+\.?\d*)"),
    'travel_arrived': re.compile(r"<(?P<timestamp>.*?)>.*\| (?P<ship_id>.*?)\[\d+\]\|.*Quantum Drive has arrived at final destination"),
}

# --- Main Parsing Functions ---

def parse_session_metadata(log_content: str) -> SessionMetadata:
    # ... (implementation from previous step)
    metadata = SessionMetadata()
    lines = log_content.splitlines()

    for line in lines:
        if "Loading level" in line:
             if all([metadata.game.build, metadata.device.processor.name, metadata.user.actor_name]):
                 break
        
        if not metadata.game.build and (match := PATTERNS['game_build'].search(line)):
            metadata.game.build = match.group(1)
        elif not metadata.game.file_version and (match := PATTERNS['file_version'].search(line)):
            metadata.game.file_version = match.group(1)
        elif not metadata.game.product_version and (match := PATTERNS['product_version'].search(line)):
            metadata.game.product_version = match.group(1)
        elif not metadata.game.branch and (match := PATTERNS['branch'].search(line)):
            metadata.game.branch = match.group(1)
        elif not metadata.game.executable and (match := PATTERNS['executable'].search(line)):
            metadata.game.executable = match.group(1).strip()
        elif not metadata.game.session_id and (match := PATTERNS['session_id'].search(line)):
            metadata.game.session_id = match.group(1)
        elif not metadata.time.log_start and (match := PATTERNS['log_start'].search(line)):
            metadata.time.log_start = match.group(1).strip()
        elif not metadata.time.build_time and (match := PATTERNS['build_time'].search(line)):
            metadata.time.build_time = match.group(1).strip()
        elif not metadata.time.local_time and (match := PATTERNS['local_time'].search(line)):
            metadata.time.local_time = match.group(1)
        elif not metadata.time.login_time and (match := PATTERNS['login_time'].search(line)):
            metadata.time.login_time = line.split('>')[0].strip('<')
        elif not metadata.device.processor.name and (match := PATTERNS['cpu_name'].search(line)):
            metadata.device.processor.name = match.group(1).strip()
        elif not metadata.device.processor.count and (match := PATTERNS['cpu_count'].search(line)):
            metadata.device.processor.count = int(match.group(1))
        elif not metadata.device.memory.total_physical_mb and (match := PATTERNS['memory'].search(line)):
            metadata.device.memory.total_physical_mb = int(match.group(1))
            metadata.device.memory.available_physical_mb = int(match.group(2))
            metadata.device.memory.usage_percent = int(match.group(3))
        elif not metadata.device.display.graphics_card and (match := PATTERNS['gpu'].search(line)):
            metadata.device.display.graphics_card = f"{match.group(1)} {match.group(2).strip()}"
        elif not metadata.device.display.display_mode and (match := PATTERNS['display_mode'].search(line)):
            metadata.device.display.display_mode = match.group(1)
        elif (match := PATTERNS['resolution'].search(line)):
            metadata.device.display.resolution = match.group(1)
        elif not metadata.device.language and (match := PATTERNS['language'].search(line)):
            metadata.device.language = match.group(1)
        elif not metadata.network.hostname and (match := PATTERNS['hostname'].search(line)):
            metadata.network.hostname = match.group(1).strip()
        elif not metadata.user.system_login and (match := PATTERNS['system_login'].search(line)):
            metadata.user.system_login = match.group(1)
        elif not metadata.user.actor_name and (match := PATTERNS['actor_name'].search(line)):
            metadata.user.actor_name = match.group(1)

    return metadata

def parse_death_events(log_content: str, actor_name: Optional[str] = None) -> List[DeathEvent]:
    # ... (implementation from previous step)
    death_events = []
    lines = log_content.splitlines()
    seen_on_foot_death_ids = set()

    for line in lines:
        ship_death_match = PATTERNS['death_in_ship'].search(line)
        if ship_death_match:
            data = ship_death_match.groupdict()
            
            # Parse ship brand and make
            ship_parts = data['ship'].split('_')
            ship_brand = ship_parts[0]
            ship_make = ' '.join(p.capitalize() for p in ship_parts[1:-1] if not p.isdigit())

            event = DeathEvent(
                timestamp=data['timestamp'],
                death_type="Die in a ship",
                player_name=data['player_name'],
                ship_brand=ship_brand,
                ship_make=ship_make,
                approx_loc=data['location']
            )
            death_events.append(event)
            continue

        foot_death_match = PATTERNS['death_on_foot'].search(line)
        if foot_death_match:
            data = foot_death_match.groupdict()
            event_id = data['id']

            if event_id not in seen_on_foot_death_ids:
                seen_on_foot_death_ids.add(event_id)
                event = DeathEvent(
                    timestamp=data['timestamp'],
                    death_type="Die on foot",
                    player_name=actor_name
                )
                death_events.append(event)

    return death_events

def parse_travel_events(log_content: str) -> List[TravelEvent]:
    """
    Parses the game.log content to extract valid quantum travel events.
    """
    travel_events = []
    lines = log_content.splitlines()
    pending_travels: Dict[str, Dict] = {}
    
    # Datetime format for parsing and calculating duration
    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    for line in lines:
        if 'QuantumTravel' not in line:
            continue

        # Check for start/update of a travel sequence
        select_match = PATTERNS['travel_select_dest'].search(line)
        calc_match = PATTERNS['travel_calc_route'].search(line)
        fuel_match = PATTERNS['travel_fuel_est'].search(line)
        
        # Any "from" event will overwrite the previous one for that ship, handling invalid attempts
        if select_match:
            data = select_match.groupdict()
            ship_id = data['ship_id']
            pending_travels[ship_id] = {'start_time': data['timestamp'], 'destination': data['destination'], 'ship': ship_id}
            continue
        
        if calc_match:
            data = calc_match.groupdict()
            ship_id = data['ship_id']
            if ship_id in pending_travels:
                pending_travels[ship_id]['start_location'] = data['start_loc']
            continue # Don't consider this a primary start event
            
        if fuel_match:
            data = fuel_match.groupdict()
            ship_id = data['ship_id']
            if ship_id in pending_travels and pending_travels[ship_id]['destination'] == data['destination']:
                pending_travels[ship_id]['fuel'] = float(data['fuel'])
            continue

        # Check for arrival
        arrive_match = PATTERNS['travel_arrived'].search(line)
        if arrive_match:
            data = arrive_match.groupdict()
            ship_id = data['ship_id']
            
            if ship_id in pending_travels:
                pending_event = pending_travels[ship_id]
                
                # Calculate duration
                start_dt = datetime.strptime(pending_event['start_time'], time_format)
                end_dt = datetime.strptime(data['timestamp'], time_format)
                duration = (end_dt - start_dt).total_seconds()
                
                event = TravelEvent(
                    start_time=pending_event['start_time'],
                    end_time=data['timestamp'],
                    duration_seconds=duration,
                    ship=pending_event.get('ship'),
                    destination=pending_event.get('destination'),
                    start_location=pending_event.get('start_location'),
                    fuel_used=pending_event.get('fuel')
                )
                travel_events.append(event)
                
                # Clear the pending event for this ship
                del pending_travels[ship_id]

    return travel_events
