/*
   esp8266 arduino iot test.
   udp client.
   simulation of mobike.
   winxos 2017-07-25
*/


#include "public.h"
#include "btn.h"


int wifi_init(int tries = 30)
{
  if (tries < 0)return -1;
  WiFi.begin(ssid, pass);
  delay(1000);
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
  if (locked_state == 0)
  {
    locked_state = 1;
    digitalWrite(LED_PIN, LOW);
    udp_send("state=locked");
    Serial.println("[debug] locked");
  }
  else
  {
    Serial.println("[debug] already locked");
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
  digitalWrite(4, HIGH);
  locked_state = 0; //default unlocked. locked manipulator.
  pinMode(2, INPUT);
  add_keydown_listener(2, &locking);
  heartbeat();
}
unsigned long last_millis = 0;

void loop()
{
  udp_scan();
  btn_scan();
  if (millis() - last_millis > heart_seconds * 1000)
  {
    last_millis = millis();
    heartbeat();
  }
}

void printWifiStatus() {
  Serial.print("[debug] SSID: ");
  Serial.println(WiFi.SSID());
  IPAddress ip = WiFi.localIP();
  Serial.print("[debug] IP Address: ");
  Serial.println(ip);
}
