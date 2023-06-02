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
SENSOR_DATA_SHEET_ID = 0
SENSOR_DATA_RANGE = "A:I"

CONFIG_SHEET = "config"
PLANT_CONFIG_RANGE = "A2:D5"
CONFIG_RANGE = "B8:B10"

SensorData = tuple[float, float, float, float]


@functools.cache
def _credentials() -> service_account.Credentials:
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )


@functools.cache
def _service():
    return googleapiclient.discovery.build("sheets", "v4", credentials=_credentials())


def append_sensor_data(time: datetime.datetime, data: tuple[float, ...]) -> int:
    request = (
        _service()
        .spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SENSOR_DATA_SHEET}!{SENSOR_DATA_RANGE}",
            valueInputOption="USER_ENTERED",
            insertDataOption="OVERWRITE",
            body={"values": [[time.isoformat(), *data]]},
        )
    )
    table_range: str = request.execute()["tableRange"]
    _, table_end = table_range.rsplit(":", 1)
    rows = int(table_end[1:]) - 1
    return rows


def remove_sensor_data(n: int) -> None:
    request = (
        _service()
        .spreadsheets()
        .batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={
                "requests": [
                    {
                        "deleteDimension": {
                            "range": {
                                "sheetId": SENSOR_DATA_SHEET_ID,
                                "dimension": "ROWS",
                                "startIndex": 1,
                                "endIndex": 1 + n,
                            }
                        }
                    }
                ]
            },
        )
    )
    request.execute()


@dataclasses.dataclass
class PlantConfig:
    max_water_ms: int
    trigger_above: float
    deactivate_below: float


@dataclasses.dataclass
class Config:
    plant_configs: dict[int, PlantConfig]
    update_delay: float
    rows_to_keep: int
    sensor_samples: int


def load_config() -> Config:
    request = (
        _service()
        .spreadsheets()
        .values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{CONFIG_SHEET}!{PLANT_CONFIG_RANGE}",
            majorDimension="ROWS",
            valueRenderOption="UNFORMATTED_VALUE",
        )
    )
    plant_config_values = request.execute()["values"]

    request = (
        _service()
        .spreadsheets()
        .values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{CONFIG_SHEET}!{CONFIG_RANGE}",
            majorDimension="COLUMNS",
            valueRenderOption="UNFORMATTED_VALUE",
        )
    )
    config_values = request.execute()["values"][0]

    return Config(
        {
            plant_id: PlantConfig(
                max_water_ms=max_water_ms,
                trigger_above=trigger_above,
                deactivate_below=deactivate_below,
            )
            for plant_id, max_water_ms, trigger_above, deactivate_below in plant_config_values
        },
        *config_values,
    )
