/*
 * Hot plate controller - dual zone (cartridges + rim band), PT100 via MAX31865, SSR burst-fire drive.
 * Target board: Arduino Nano / Uno (or ESP32 with pin changes).
 * Libraries: Adafruit MAX31865.
 *
 * SAFETY: this software limit is NOT the safety system. A hardware manual-reset thermostat
 * (see docs/safety.md) must independently cut mains to both heaters.
 *
 * Serial commands (115200 baud, newline terminated):
 *   S <degC>     set target                 R           run   X   stop (heaters off)
 *   O <zone> <K> set rim-sensor offset (zone 1) or centre offset (zone 0), degC
 *   ? / (nothing) -> status line streamed once per second as CSV:
 *   t_s,setpoint,T_centre,T_rim,duty_cart,duty_band,state
 */
#include <SPI.h>
#include <Adafruit_MAX31865.h>

// ---------------- pins ----------------
const uint8_t CS_CENTRE = 10;   // MAX31865 #1: PT100 3 mm below top at (0,+17.5) mm
const uint8_t CS_RIM    = 9;    // MAX31865 #2: PT100 3 mm below top at (58,-17.5) mm
const uint8_t SSR_CART  = 5;    // SSR for the 3 cartridge heaters (zone 0)
const uint8_t SSR_BAND  = 6;    // SSR for the rim band heater (zone 1)
const uint8_t LED_RUN   = 7;
const uint8_t BUZZER    = 8;
const uint8_t ESTOP_IN  = 4;    // reads the hardware safety chain contactor feedback (LOW = chain closed / OK)

Adafruit_MAX31865 rtdC(CS_CENTRE), rtdR(CS_RIM);
const float RREF = 430.0, RNOMINAL = 100.0;     // 430 ohm reference for PT100 board

// ---------------- limits ----------------
const float T_MAX_SET   = 400.0;
const float T_HARD_CUT  = 415.0;   // software over-temperature trip (hardware thermostat is set higher, ~430 C)
const float T_MIN_VALID = -10.0;
const float RATE_LIMIT  = 6.0;     // K/s: reject impossible jumps (open sensor, noise)
const unsigned long WINDOW_MS = 1000;  // burst-fire window: 100 half-cycles at 50 Hz = 1 % resolution

// ---------------- control ----------------
struct Pid {
  float kp, ki, kd;     // W/K, W/(K s), W s/K  (power domain, see control/control_sim.py)
  float I = 0, prev = NAN;
};
Pid pid = {80.0, 0.15, 100.0};
const float P_CART_MAX = 450.0, P_BAND_MAX = 350.0, P_TOTAL = P_CART_MAX + P_BAND_MAX;
// Fraction of the commanded power that goes to the rim band. 0.5 at steady state (from the 3D model);
// during a ramp both zones are heated in proportion to installed power so the rim does not lag.
float rimFractionSteady = 0.50;

float setpoint = 25.0, offC = 0.0, offR = 0.0;
enum State { IDLE, RUNNING, FAULT } state = IDLE;
float tC = NAN, tR = NAN, dutyCart = 0, dutyBand = 0;
unsigned long tLast = 0, winStart = 0;

bool sensorOk(float v, float prevv) {
  if (isnan(v) || v < T_MIN_VALID || v > 500.0) return false;
  if (!isnan(prevv) && fabs(v - prevv) > RATE_LIMIT) return false;
  return true;
}

void heatersOff() { digitalWrite(SSR_CART, LOW); digitalWrite(SSR_BAND, LOW); dutyCart = dutyBand = 0; }

void fault(const char *why) {
  heatersOff(); state = FAULT; pid.I = 0;
  Serial.print(F("FAULT: ")); Serial.println(why);
  digitalWrite(BUZZER, HIGH);
}

void setup() {
  pinMode(SSR_CART, OUTPUT); pinMode(SSR_BAND, OUTPUT); heatersOff();
  pinMode(LED_RUN, OUTPUT); pinMode(BUZZER, OUTPUT); pinMode(ESTOP_IN, INPUT_PULLUP);
  Serial.begin(115200);
  rtdC.begin(MAX31865_3WIRE); rtdR.begin(MAX31865_3WIRE);   // use MAX31865_4WIRE if the 4-wire jumpers are fitted
  Serial.println(F("t_s,setpoint,T_centre,T_rim,duty_cart,duty_band,state"));
}

void readSensors() {
  float c = rtdC.temperature(RNOMINAL, RREF) + offC;
  float r = rtdR.temperature(RNOMINAL, RREF) + offR;
  uint8_t fc = rtdC.readFault(), fr = rtdR.readFault();
  if (fc || fr) { rtdC.clearFault(); rtdR.clearFault(); fault("RTD fault flag"); return; }
  if (!sensorOk(c, tC) || !sensorOk(r, tR)) {
    if (!isnan(tC)) { fault("sensor out of range or jumped"); return; }
  }
  tC = c; tR = r;
}

void parseSerial() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n'); line.trim();
  if (line.length() == 0) return;
  char c = line.charAt(0);
  if (c == 'S') { float v = line.substring(1).toFloat(); setpoint = constrain(v, 25.0, T_MAX_SET); }
  else if (c == 'R') { if (state != FAULT) { state = RUNNING; pid.I = 0; pid.prev = NAN; } }
  else if (c == 'X') { state = IDLE; heatersOff(); digitalWrite(BUZZER, LOW); }
  else if (c == 'O') {
    int z = line.substring(1, 3).toInt(); float v = line.substring(3).toFloat();
    if (z == 0) offC = v; else offR = v;
  }
}

void controlStep(float dt) {
  // The loop regulates the CENTRE sensor; the rim sensor is monitored and trimmed through the band share.
  float e = setpoint - tC;
  float dmeas = isnan(pid.prev) ? 0 : (tC - pid.prev) / dt;
  pid.prev = tC;
  float Pun = pid.kp * e + pid.I - pid.kd * dmeas;
  float P = constrain(Pun, 0.0, P_TOTAL);
  // conditional integration + anti-windup
  if (fabs(e) < 8.0 && ((Pun > 0 && Pun < P_TOTAL) || (Pun <= 0 && e > 0) || (Pun >= P_TOTAL && e < 0)))
    pid.I = constrain(pid.I + pid.ki * e * dt, 0.0, P_TOTAL);

  // Zone split: ramp (large error) -> proportional to installed power; near setpoint -> steady-state share,
  // then a slow trim so that T_rim - T_centre follows the calibrated target (0 after offsets are applied).
  float share = (fabs(e) > 15.0) ? (P_BAND_MAX / P_TOTAL) : rimFractionSteady;
  float rimErr = tC - tR;                        // >0 : rim is colder than centre
  rimFractionSteady = constrain(rimFractionSteady + 0.002 * rimErr * dt, 0.30, 0.70);
  float Pb = constrain(P * share, 0.0, P_BAND_MAX);
  float Pc = constrain(P - Pb, 0.0, P_CART_MAX);
  dutyBand = Pb / P_BAND_MAX; dutyCart = Pc / P_CART_MAX;
}

void driveSSR() {
  unsigned long now = millis();
  if (now - winStart >= WINDOW_MS) winStart += WINDOW_MS;
  unsigned long pos = now - winStart;
  digitalWrite(SSR_CART, (state == RUNNING && pos < dutyCart * WINDOW_MS) ? HIGH : LOW);
  digitalWrite(SSR_BAND, (state == RUNNING && pos < dutyBand * WINDOW_MS) ? HIGH : LOW);
}

void loop() {
  parseSerial();
  unsigned long now = millis();
  if (now - tLast >= 1000) {
    float dt = (now - tLast) / 1000.0; tLast = now;
    readSensors();
    if (state != FAULT) {
      if (tC > T_HARD_CUT || tR > T_HARD_CUT) fault("software over-temperature");
      else if (digitalRead(ESTOP_IN) == HIGH && state == RUNNING) fault("hardware safety chain open");
      else if (state == RUNNING) controlStep(dt);
    }
    digitalWrite(LED_RUN, state == RUNNING);
    Serial.print(now / 1000); Serial.print(','); Serial.print(setpoint, 1); Serial.print(',');
    Serial.print(tC, 2); Serial.print(','); Serial.print(tR, 2); Serial.print(',');
    Serial.print(dutyCart, 3); Serial.print(','); Serial.print(dutyBand, 3); Serial.print(',');
    Serial.println(state == IDLE ? "IDLE" : state == RUNNING ? "RUN" : "FAULT");
  }
  if (state != RUNNING) heatersOff(); else driveSSR();
}
