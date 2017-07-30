/*
   esp8266 arduino iot test.
   udp client.
   simulation of mobike.
   winxos 2017-07-25
*/
#include "public.h"
#include "btn.h"
#include <SimpleDHT.h>
int pinDHT11 = 14;
SimpleDHT11 dht11;

STATE behavior_state = IDLE;
EVENT event_state = EVENT_IDLE;
int wifi_init(int tries = 30)
{
  if (tries < 0)return -1;
  WiFi.begin(ssid, pass);
  delay(500);
  Serial.print("[debug] connecting to ");
  Serial.print(ssid);
  Serial.println(" ...");
  if (WiFi.status() != WL_CONNECTED) {
    wifi_init(tries - 1);
  }
  return 0;
}

void heartbeat()
{
  udp_send("");
}

void locking()
{
  event_state = EVENT_LOCKING;
  Serial.println("[debug] locking");
}
void samping()
{
  byte temperature = 0;
  byte humidity = 0;
  if ( dht11.read(pinDHT11, &temperature, &humidity, NULL) == SimpleDHTErrSuccess) {
    String s = "data=";
    s += (int)temperature;
    s += " ";
    s += (int)humidity;
    Serial.println(s);
    udp_send((char*)s.c_str());
  }
}
unsigned long last_millis = 0, last_sampling_millis = 0;
void state_loop()
{
  switch (behavior_state)
  {
    case IDLE:
      if (millis() - last_millis > heart_seconds * 1000)
      {
        last_millis = millis();
        heartbeat();
      }
      if (event_state == EVENT_UNLOCKING)
      {
        digitalWrite(LED_PIN, HIGH);
        Serial.println("[debug] unlocked");
        udp_send("state=unlocked");
        behavior_state = USING; //IF SUCCESS
        event_state = EVENT_IDLE;
      }
      break;
    case USING:
      if (millis() - last_sampling_millis > sampling_seconds * 1000)
      {
        last_sampling_millis = millis();
        samping();
      }
      if (event_state == EVENT_LOCKING)
      {
        digitalWrite(LED_PIN, LOW);
        udp_send("state=locked");
        Serial.println("[debug] locked");
        behavior_state = IDLE;
        event_state = EVENT_IDLE;
      }
      break;
    default:
      Serial.println("error");
      break;
  }
}
void setup()
{
  Serial.begin(115200);
  while (!Serial);
  if (wifi_init() < 0)
  {
    Serial.print("[error] connecting failed.");
    return;
  }
  Serial.println("[debug] Connected to wifi");
  printWifiStatus();
  Serial.print("[debug] local listen port ");
  Serial.println(local_port);
  Udp.begin(local_port);
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);
  pinMode(2, INPUT);
  add_keydown_listener(2, &locking);
  udp_send("online");
}

void loop()
{
  udp_scan();
  btn_scan();
  state_loop();
}

void printWifiStatus() {
  Serial.print("[debug] SSID: ");
  Serial.println(WiFi.SSID());
  IPAddress ip = WiFi.localIP();
  Serial.print("[debug] IP Address: ");
  Serial.println(ip);
}
