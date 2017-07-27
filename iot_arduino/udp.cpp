#include "public.h"
byte udp_buf[buf_size] = {0}; //buffer to hold incoming and outgoing packets
WiFiUDP Udp;
void udp_send(char *s)
{
  String ss = "id=";
  ss += device_id;
  ss+=";";
  ss+=s;
  Udp.beginPacket(server_host, server_port);
  Udp.write((char*)ss.c_str());
  Udp.endPacket();
}
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
    for (int i = 0; i < udp_len; ++i)
    {
      Serial.print(udp_buf[i], HEX);
      Serial.print(' ');
    }
    Serial.println("[data end]");
    run_cmd(udp_buf);
  }
}
