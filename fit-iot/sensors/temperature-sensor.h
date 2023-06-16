#ifndef __TEMPERATURE_SENSOR_H_
#define __TEMPERATURE_SENSOR_H_

#include "../environment.h"
extern env myenv;

/**
 * Return the temperature inside the room.
 */
double get_temperature() { return myenv.temperature_in; }

#endif