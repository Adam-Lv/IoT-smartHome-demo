#ifndef __DEVICES_H_
#define __DEVICES_H_

typedef struct Lamp
{
  int state;
} Lamp;

typedef struct AirConditioner
{ 
  /* 0 is off, 1 is cooling mode, 2 is heating mode */
  int state;
} AirConditioner;

#endif