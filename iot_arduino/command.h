int is_invalid(byte*buf)
{
  return 0;
}

void _dw(byte* a)
{
  digitalWrite(a[0], a[1]);
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
  Serial.println(buf[1], HEX);
  if (buf[1] < 4)
  {
    ops[buf[1]](&buf[2]);
  }
  return 0;
}

