import datetime
import os
import time
from plantotron import _spreadsheet
import simple_rpc


DEVICE = "/dev/ttyACM0"
INTERFACE_FILE = os.path.join(os.path.dirname(__file__), "interface.yml")
SENSOR_IDS = (0, 1, 2, 3)

class Application:
    def __init__(self) -> None:
        self.loop_delay = 60 * 15
        self.interface = simple_rpc.Interface(DEVICE, autoconnect=False)
        with open(INTERFACE_FILE) as interface_file:
            self.interface.open(interface_file)

    def _read_all_sensors(self) -> _spreadsheet.SensorData:
        return tuple(self.interface.get_sensor(sensor_id) for sensor_id in SENSOR_IDS)

    def _average_sensor_readings(
        self, n: int = 10, delta_t: float = 0.1
    ) -> _spreadsheet.SensorData:
        data = [self._read_all_sensors()]
        for _ in range(n - 1):
            time.sleep(delta_t)
            data.append(self._read_all_sensors())
        return tuple(sum(samples) for samples in zip(*data))

    def loop(self) -> None:
        now = datetime.datetime.now()
        data = self._average_sensor_readings()
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
