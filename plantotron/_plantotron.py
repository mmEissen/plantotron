import datetime
import os
import time
from plantotron import _spreadsheet
import simple_rpc


DEVICE = "/dev/ttyACM0"
INTERFACE_FILE = os.path.join(os.path.dirname(__file__), "interface.yml")

class Application:
    def __init__(self) -> None:
        self.loop_delay = 60
        self.interface = simple_rpc.Interface(DEVICE, autoconnect=False)
        with open(INTERFACE_FILE) as interface_file:
            self.interface.open(interface_file)

    def loop(self) -> None:
        now = datetime.datetime.now()
        data = tuple(self.interface.get_sensor(i) for i in range(4))
        _spreadsheet.append_sensor_data(now, data)

    def run_forever(self) -> None:
        while True:
            self.loop()
            time.sleep(self.loop_delay)


def main() -> None:
    app = Application()
    try:
        app.run_forever()
    finally:
        if app.interface.is_open():
            app.interface.close()
