import time


class Application:
    def __init__(self) -> None:
        self.loop_delay = 60

    def loop(self) -> None:
        pass

    def run_forever(self) -> None:
        while True:
            self.loop()
            time.sleep(self.loop_delay)


def main() -> None:
    app = Application()
    app.run_forever()
