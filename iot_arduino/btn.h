/*
  arduino key model
  can bind D0-D13 A0-A5
  winxos 2014-10-23
*/
#include <arduino.h>
#define KEYDOWN_VOL LOW

#define MAX_KEYS 20
#define TRIGGER_CYC 30
#define TRIGGER_DOWN 0
#define TRIGGER_UP 1

typedef unsigned char u8;
typedef void(*CALLBACK)();

CALLBACK cbs[MAX_KEYS]; //callback array
u8 key_buf[MAX_KEYS]; //software key buffer
long key_binded = 0; //binded bit check
long key_trig_type = 0;

void set_bit(long &data, u8 port)
{
  data |= (1 << port);
}
void clear_bit(long &data, u8 port)
{
  data &= ~(1 << port);
}
u8 get_bit(long data, u8 port)
{
  return (data & (1 << port)) > 0;
}
static void add_listener(u8 port, void (*fun)(), u8 type)
{
  if (port > MAX_KEYS)
    return;
  set_bit(key_binded, port);
  if (type == TRIGGER_UP)
    set_bit(key_trig_type, port);
  else
    clear_bit(key_trig_type, port);
  cbs[port] = fun;
  Serial.println(key_trig_type, HEX);
  Serial.println(key_binded, HEX);
}
void add_keydown_listener(u8 port, void (*fun)())
{
  add_listener(port, fun, TRIGGER_DOWN);
}
void add_keyup_listener(u8 port, void (*fun)())
{
  add_listener(port, fun, TRIGGER_UP);
}
void remove_listener(u8 port)
{
  if (port > MAX_KEYS)
    return;
  clear_bit(key_binded, port);
}
void btn_scan()
{
  for (u8 i = 0; i < MAX_KEYS; i++)
  {
    if (get_bit(key_binded, i)) //binded
    {
      if (digitalRead(i) == KEYDOWN_VOL)
      {
        if (key_buf[i] < 250)
          key_buf[i]++;
        if (key_buf[i] == TRIGGER_CYC &&
            get_bit(key_trig_type, i) == TRIGGER_DOWN)
        {
          cbs[i]();//keydown callback
        }
      }
      else
      {
        if (key_buf[i] > TRIGGER_CYC &&
            get_bit(key_trig_type, i) == TRIGGER_UP)
        {
          cbs[i]();//keyup callback
        }
        key_buf[i] = 0;
      }
    }
  }
}
