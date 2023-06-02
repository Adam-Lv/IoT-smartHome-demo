#ifndef __ENVIRONMENT_H_
#define __ENVIRONMENT_H_
#include "devices/devices.h"

typedef struct env
{
  int day;
  int hour;
  int light;
  double temperature_out;
  double temperature_in;
  Lamp lamp;
  AirConditioner air_conditioner;
} env;

#endif
