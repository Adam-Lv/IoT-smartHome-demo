#ifndef __LIGHT_SENSOR_H_
#define __LIGHT_SENSOR_H_

#include "../environment.h"
extern env myenv;

/**
 * Return the litght intensity of the enviroment.
 */
int get_light() { return myenv.light; }

#endif