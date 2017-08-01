#pragma once

#include <arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiUDP.h>
extern WiFiUDP Udp;

#define LOCK_PIN 2
#define LED_PIN 4
//  your network SSID (name)
//#define  ssid "robot" 
//#define  pass "x11111111"   
#define  ssid "Aiesst"  
#define  pass "11111111"    
// local port to listen for UDP packets  
#define  local_port 12345    

#define  server_host "192.168.199.102"
//#define  server_host "iot.aistl.com"
#define server_port 9999

#define  device_id "0280000001"

#define  buf_size 128
extern byte udp_buf[buf_size];
//seconds
#define  heart_seconds 300
#define  sampling_seconds 30
enum STATE{IDLE,USING};
extern STATE behavior_state;
enum EVENT{EVENT_IDLE,EVENT_UNLOCKING,EVENT_LOCKING};
extern EVENT event_state;
int run_cmd(byte* buf);

void udp_scan();
void udp_send(char *s);
