import dataclasses
import datetime
from typing import List, Optional, Union

from typing_extensions import Literal


@dataclasses.dataclass
class ObservationGoal:
    observation_goal: str
    privacy_declaration: str
    legal_ground: str


@dataclasses.dataclass
class LatLong:
    latitude: Union[float, str]
    longitude: Union[float, str]


@dataclasses.dataclass
class PostcodeHouseNumber:
    postcode: str
    house_number: Union[int, str]
    suffix: str = ''


@dataclasses.dataclass
class Location:
    lat_long: Optional[LatLong]
    postcode_house_number: Optional[PostcodeHouseNumber]
    description: str
    regions: str


@dataclasses.dataclass
class PersonData:
    organisation: str
    email: str
    telephone: str
    website: str
    first_name: str
    last_name_affix: str
    last_name: str


@dataclasses.dataclass
class SensorData:
    owner: PersonData
    reference: str
    type: str
    location: Location
    datastream: str
    observation_goals: List[ObservationGoal]
    themes: str
    contains_pi_data: Literal['Ja', 'Nee']
    active_until: Union[datetime.date, str]
    projects: List[str]
    row_number: Optional[int] = None
