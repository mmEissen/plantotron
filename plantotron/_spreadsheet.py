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
SENSOR_DATA_RANGE = "A:E"


@functools.cache
def _credentials() -> service_account.Credentials:
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )


@functools.cache
def _service():
    return googleapiclient.discovery.build("sheets", "v4", credentials=_credentials())


def append_sensor_data(time: datetime.datetime, data: tuple[int, int, int, int]):
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

