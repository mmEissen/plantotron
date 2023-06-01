import dataclasses
import datetime
import functools
import os
from google.oauth2 import service_account
import googleapiclient.discovery
from googleapiclient import errors

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "credentials", "service_account.json"
)
SPREADSHEET_ID = "1zdE2TLWVGPYxgmjvDDOAKpG-9qtT27OLOew0wa4K8qI"
SENSOR_DATA_SHEET = "sensor_data"
SENSOR_DATA_RANGE = "A:I"

CONFIG_SHEET = "config"
CONFIG_RANGE = "A2:E5"

SensorData = tuple[float, float, float, float]

@functools.cache
def _credentials() -> service_account.Credentials:
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )


@functools.cache
def _service():
    return googleapiclient.discovery.build("sheets", "v4", credentials=_credentials())


def append_sensor_data(time: datetime.datetime, data: tuple[float, ...]):
    request = _service().spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SENSOR_DATA_SHEET}!{SENSOR_DATA_RANGE}",
        valueInputOption="USER_ENTERED",
        insertDataOption="OVERWRITE",
        body={
            "values": [[
                time.isoformat(),
                *data
            ]]
        }
    )
    return request.execute()


@dataclasses.dataclass
class PIDConfig:
    setpoint: float
    proportional_gain: float
    integral_gain: float
    derivative_gain: float


@dataclasses.dataclass
class Config:
    pid_configs: dict[int, PIDConfig]


def load_config() -> Config:
    request = _service().spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{CONFIG_SHEET}!{CONFIG_RANGE}",
        majorDimension="ROWS",
        valueRenderOption="UNFORMATTED_VALUE",
    )
    response = request.execute()
    return Config(
        pid_configs={
            plant_id: PIDConfig(
                setpoint=setpoint,
                proportional_gain=p,
                integral_gain=i,
                derivative_gain=d,
            )
            for plant_id, setpoint, p, i, d in response["values"]
        }
    )
