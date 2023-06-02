#ifndef __TEMPERATURE_SENSOR_H_
#define __TEMPERATURE_SENSOR_H_

#include "../environment.h"
extern env myenv;

/**
 * Return the temprature inside the room.
 */
double get_temprature() { return myenv.temperature_in; }

#endif