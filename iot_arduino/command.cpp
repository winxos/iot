#pragma once
#include "public.h"
byte locked_state = 0;
int is_invalid(byte*buf)
{
  return 0;
}

void _dw(byte* a)
{
  if(a[0]==LOCK_PIN) //LOCK or UNLOCK
  {
    if(a[1]==0)//UNLOCK
    {
      locked_state = 0;
      digitalWrite(LED_PIN,HIGH);
      Serial.println("[debug] unlocked");
      udp_send("state=unlocked");
    }
    else //remote lock
    {
      locked_state = 1;
      digitalWrite(LED_PIN,LOW);
    }
  }
}
void _dr(byte* a)
{}
void _aw(byte* a)
{}
void _ar(byte* a)
{}
enum {DW, DR, AW, AR};
typedef void (*pF)(byte*);
pF ops[4] = {_dw, _dr, _aw, _ar};
int run_cmd(byte* buf)
{
  if (is_invalid(buf))return -1;
  if (buf[1] < 4)
  {
    ops[buf[1]](&buf[2]);
  }
  return 0;
}

