import datetime
import os
import time
from plantotron import _spreadsheet
import simple_rpc
import simple_pid


DEVICE = "/dev/ttyACM0"
INTERFACE_FILE = os.path.join(os.path.dirname(__file__), "interface.yml")


class Application:
    def __init__(self, config: _spreadsheet.Config) -> None:
        self.loop_delay = 60 * 15
        self.interface = simple_rpc.Interface(DEVICE, autoconnect=False)
        with open(INTERFACE_FILE) as interface_file:
            self.interface.open(interface_file)
        self.config = _spreadsheet.load_config()
        self.pid_controllers = {
            plant_id: simple_pid.PID() for plant_id in self.config.pid_configs
        }
        self._configure_pid_controllers()

    def _configure_pid_controllers(self) -> None:
        for plant_id, pid_config in self.pid_configs:
            try:
                pid_controller = self.config.pid_configs[plant_id]
            except KeyError:
                pid_controller = self.pid_controllers[plant_id] = simple_pid.PID()
            pid_controller.Kp = pid_config.proportional_gain
            pid_controller.Ki = pid_config.integral_gain
            pid_controller.Kd = pid_config.derivative_gain

    def plant_ids(self) -> tuple[int, int, int, int]:
        return tuple(sorted(self.config.pid_configs.keys()))

    def _read_all_sensors(self) -> _spreadsheet.SensorData:
        return tuple(
            self.interface.get_sensor(sensor_id) for sensor_id in self.plant_ids()
        )

    def _average_sensor_readings(
        self, n: int = 10, delta_t: float = 0.1
    ) -> _spreadsheet.SensorData:
        data = [self._read_all_sensors()]
        for _ in range(n - 1):
            time.sleep(delta_t)
            data.append(self._read_all_sensors())
        return tuple(sum(samples) / n for samples in zip(*data))

    def loop(self) -> None:
        self.config = _spreadsheet.load_config()
        self._configure_pid_controllers()
        now = datetime.datetime.now()
        data = self._average_sensor_readings()
        controls = tuple(
            self.pid_controllers[plant_id](value)
            for plant_id, value in zip(self.plant_ids(), data)
        )
        _spreadsheet.append_sensor_data(now, tuple(*data, *controls))
        

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
