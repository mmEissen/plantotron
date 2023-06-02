import datetime
import os
import time
from plantotron import _spreadsheet
import simple_rpc
import simple_pid


DEVICE = "/dev/ttyACM0"
INTERFACE_FILE = os.path.join(os.path.dirname(__file__), "interface.yml")


class Application:
    def __init__(self) -> None:
        self.interface = simple_rpc.Interface(DEVICE, autoconnect=False)
        with open(INTERFACE_FILE) as interface_file:
            self.interface.open(interface_file)
        self.config = _spreadsheet.load_config()

    def plant_ids(self) -> tuple[int, int, int, int]:
        return tuple(sorted(self.config.pid_configs.keys()))

    def _read_all_sensors(self) -> _spreadsheet.SensorData:
        return tuple(
            self.interface.get_sensor(sensor_id) for sensor_id in self.plant_ids()
        )

    def _average_sensor_readings(
        self, delta_t: float = 0.1
    ) -> _spreadsheet.SensorData:
        n = self.config.sensor_samples
        data = [self._read_all_sensors()]
        for _ in range(n - 1):
            time.sleep(delta_t)
            data.append(self._read_all_sensors())
        return tuple(sum(samples) / n for samples in zip(*data))

    def loop(self) -> None:
        self.config = _spreadsheet.load_config()
        now = datetime.datetime.now()
        data = self._average_sensor_readings()
        current_rows = _spreadsheet.append_sensor_data(now, data)
        if current_rows > self.config.rows_to_keep:
            _spreadsheet.remove_sensor_data(current_rows - self.config.rows_to_keep)
        

    def run_forever(self) -> None:
        while True:
            self.loop()
            time.sleep(self.config.update_delay)


def main() -> None:
    app = Application()
    try:
        app.run_forever()
    finally:
        if app.interface.is_open():
            app.interface.close()
