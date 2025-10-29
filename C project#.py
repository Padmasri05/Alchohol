#include <SoftwareSerial.h>

// -------------------- PIN DEFINITIONS --------------------
#define MQ3_PIN A0          // MQ-3 Alcohol Sensor (Analog)
#define RELAY_PIN 8         // Relay control for ignition/motor

// GSM and GPS connections
SoftwareSerial gsm(9, 10);   // RX, TX for SIM800C
SoftwareSerial gps(11, 12);  // RX, TX for GPS NEO-6M

// -------------------- SETTINGS --------------------
int alcoholThreshold = 300;   // Adjust based on MQ-3 calibration
String phoneNumber = "+917013475639";  // Replace with your phone number

// Relay Logic
const int RELAY_ON = LOW;   // Relay ON when IN = LOW (active LOW)
const int RELAY_OFF = HIGH; // Relay OFF when IN = HIGH

// Flag to prevent multiple SMS in short time
bool alcoholAlertSent = false;

// -------------------- INITIALIZATION --------------------
void setup() {
  Serial.begin(9600);
  gsm.begin(9600);
  gps.begin(9600);

  pinMode(MQ3_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);

  // Initially motor OFF
  digitalWrite(RELAY_PIN, RELAY_OFF);

  Serial.println("🪖 Smart Helmet System Started");
  sendSMS("🪖 SMART HELMET SYSTEM STARTED ✅");
}

// -------------------- MAIN LOOP --------------------
void loop() {
  int mqValue = analogRead(MQ3_PIN);   // Read alcohol sensor
  bool alcoholDetected = (mqValue > alcoholThreshold);

  Serial.print("Alcohol Value: ");
  Serial.println(mqValue);

  if (alcoholDetected) {
    // Alcohol detected → Stop motor and send alert
    digitalWrite(RELAY_PIN, RELAY_OFF);
    Serial.println("🚫 ALCOHOL DETECTED! Ignition Disabled.");

    if (!alcoholAlertSent) {
      sendAlcoholAlert();
      alcoholAlertSent = true; // Prevent repeated SMS
    }
  } else {
    // Safe → Motor ON
    digitalWrite(RELAY_PIN, RELAY_ON);
    Serial.println("✅ SAFE TO RIDE - Ignition ON");
    alcoholAlertSent = false; // Reset alert flag
  }

  delay(1000); // Update every 2 seconds
}

// -------------------- SEND SMS FUNCTION --------------------
void sendSMS(String message) {
  gsm.println("AT+CMGF=1"); // Text mode
  delay(500);
  gsm.print("AT+CMGS=\"");
  gsm.print(phoneNumber);
  gsm.println("\"");
  delay(500);
  gsm.print(message);
  delay(500);
  gsm.write(26); // CTRL+Z to send
  delay(1000);
}

// -------------------- SEND ALCOHOL ALERT WITH GPS --------------------
void sendAlcoholAlert() {
  String gpsData = getGPSLocation();
  String alert = "🚫 ALCOHOL DETECTED! Ignition Disabled. Location: " + gpsData;
  sendSMS(alert);
}

// -------------------- GPS LOCATION FUNCTION --------------------
String getGPSLocation() {
  String data = "";
  unsigned long startTime = millis();

  while (millis() - startTime < 5000) {  // Wait 5 sec for GPS data
    while (gps.available()) {
      char c = gps.read();
      data += c;
    }
  }

  if (data.length() < 10) return "No GPS Data";

  // Extract basic coordinates from GPGGA sentence
  int latIndex = data.indexOf("GPGGA");
  if (latIndex != -1) {
    String sub = data.substring(latIndex, latIndex + 80);
    return sub;
  }

  return "GPS Signal Weak";
}
