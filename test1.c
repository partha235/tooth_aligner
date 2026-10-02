// this program is for transmitter esp8266. 
#include <ESP8266WiFi.h>

// =====================================================
// WIFI
// =====================================================

const char* ssid = "aligner_box";
const char* password = "123456789";

// Box ESP32 IP address
IPAddress boxIP(192, 168, 4, 1);

// =====================================================
// MICRO SWITCH
// =====================================================

#define SWITCH_PIN 2       // ESP-01 GPIO2

// =====================================================
// SETTINGS
// =====================================================

WiFiClient client;

const uint16_t BOX_PORT = 5000;

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL = 1000;   // 1 second


// =====================================================
// CONNECT TO WIFI
// =====================================================

void connectWiFi()
{
  Serial.println();
  Serial.print("Connecting to box WiFi");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");

  Serial.print("ESP-01 IP: ");
  Serial.println(WiFi.localIP());

  Serial.print("Box IP: ");
  Serial.println(boxIP);
}


// =====================================================
// SEND SENSOR STATE
// =====================================================

void sendState()
{
  bool pressed = (digitalRead(SWITCH_PIN) == LOW);

  String state;

  if (pressed)
  {
    state = "PRESSED";
  }
  else
  {
    state = "RELEASED";
  }

  Serial.print("Switch: ");
  Serial.println(state);


  // Connect to ESP32 box
  if (client.connect(boxIP, BOX_PORT))
  {
    client.println(state);

    Serial.print("Sent to box: ");
    Serial.println(state);

    client.stop();
  }
  else
  {
    Serial.println("ERROR: Cannot connect to box");
  }
}


// =====================================================
// SETUP
// =====================================================

void setup()
{
  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("==============================");
  Serial.println("ALIGNER ESP-01 TRANSMITTER");
  Serial.println("==============================");

  // Internal pull-up
  pinMode(SWITCH_PIN, INPUT_PULLUP);

  connectWiFi();
}


// =====================================================
// LOOP
// =====================================================

void loop()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("WiFi lost!");
    connectWiFi();
  }

  if (millis() - lastSend >= SEND_INTERVAL)
  {
    lastSend = millis();

    sendState();
  }
}