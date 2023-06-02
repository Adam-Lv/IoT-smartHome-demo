#ifndef __CONTROLER_H_
#define __CONTROLER_H_

#include "../environment.h"

extern env myenv;

/* Turn on the lamp */
void turn_on_lamp() { myenv.lamp.state = 1; }

/* Turn off the lamp */
void turn_off_lamp() { myenv.lamp.state = 0; }

/* Return the state of the lamp: 1 is on, 0 is off */
int get_lamp_state() { return myenv.lamp.state; }

void turn_off_ac() { myenv.air_conditioner.state = 0; }

void turn_ac_cool() { myenv.air_conditioner.state = 1; }

void turn_ac_heat() { myenv.air_conditioner.state = 2; }

int get_ac_state() { return myenv.air_conditioner.state; }
#endif