#include <simpleRPC.h>

#define PLANT_COUNT (4)
#define CLOSE_TIME_THRESHOLD (5000)


const uint8_t sensor_pins[] = {A0, A1, A2, A3};
const uint8_t valve_pins[] = {9, 10, 11, 12};
unsigned long when_to_close[] = {0, 0, 0, 0};

void setup() {
  for (int i = 0; i < PLANT_COUNT; ++i) {
    pinMode(valve_pins[i], OUTPUT);
  }
  Serial.begin(9600);
}


int get_sensor(uint8_t plant_id) {
  if (plant_id >= PLANT_COUNT) {
    return -1;
  }
  return analogRead(sensor_pins[plant_id]);
}


void open_valve(uint8_t plant_id, uint16_t milliseconds) {
  when_to_close[plant_id] = millis() + milliseconds;
  digitalWrite(valve_pins[plant_id], HIGH);
}


void maybe_close_valves() {
  unsigned long now = millis();
  for (int i = 0; i < PLANT_COUNT; ++i) {
    if (now - when_to_close[i] < CLOSE_TIME_THRESHOLD) {
      digitalWrite(valve_pins[i], LOW);
    }
  }
}


void loop() {
  interface(
    Serial,
    get_sensor,
    "get_sensor: Get sensor value. @plant_id: The plant ID of which to read the sensor value @return: The value of the sensor, or -1 if the plant ID is out of range.",
    open_valve,
    "open_valve: Open a valve. @plant_id: The plant ID for which to open the valve @milliseconds: The number of milliseconds to keep the sensor open for"
  );
  maybe_close_valves();
}


