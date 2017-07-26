/*
   esp8266 arduino iot test.
   udp client.
   simulation of mobike.
   winxos 2017-07-25
*/

#include <ESP8266WiFi.h>
#include <WiFiUDP.h>
#include "command.h"
WiFiUDP Udp;


const char* ssid = "robot";  //  your network SSID (name)
const char* pass = "x11111111";       // your network password
unsigned int local_port = 12345;      // local port to listen for UDP packets

const char* server_host = "192.168.3.122";
//const char* server_host = "iot.aistl.com";
unsigned int server_port = 9999;

const char* device_id = "0280000001";

const unsigned int buf_size = 128;
byte udp_buf[buf_size]; //buffer to hold incoming and outgoing packets
const unsigned int heart_seconds = 30; //seconds

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
void udp_send(char *s)
{
  Udp.beginPacket(server_host, server_port);
  Udp.write(s);
  Udp.endPacket();
}

void heartbeat()
{
  String s = "id=";
  s += device_id;
  udp_send((char*)s.c_str());
}
unsigned long last_millis = 0;
void udp_scan()
{
  int udp_len = Udp.parsePacket();
  if ( udp_len ) {
    Serial.print("[debug] Packet of ");
    Serial.print(udp_len);
    Serial.print(" received from ");
    Serial.print(Udp.remoteIP());
    Serial.print(":");
    Serial.println(Udp.remotePort());
    Udp.read(udp_buf, udp_len); // read the packet into the buffer
    Serial.print("[debug] [udp data]");
    Serial.print((char*)udp_buf);
    Serial.println("[data end]");
    analyze(udp_buf);
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
  pinMode(2, INPUT);
}
void loop()
{
  udp_scan();
  if (millis() - last_millis > heart_seconds * 1000)
  {
    last_millis = millis();
    heartbeat();
  }
  if (digitalRead(2) == HIGH && digitalRead(2) == LOW)
  {
    udp_send("locked");
    digitalWrite(4,LOW);
  }
}
void analyze(byte* buf)
{
  run_cmd(buf);
  memset(buf, 0, buf_size);
}
void printWifiStatus() {
  Serial.print("[debug] SSID: ");
  Serial.println(WiFi.SSID());
  IPAddress ip = WiFi.localIP();
  Serial.print("[debug] IP Address: ");
  Serial.println(ip);
}
