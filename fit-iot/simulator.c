#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "contiki-lib.h"
#include "contiki-net.h"
#include "contiki.h"
#include "dev/slip.h"
#include "environment.h"
#include "httpd-simple.h"
#include "net/ip/uip-debug.h"
#include "net/ip/uip.h"
#include "net/ipv6/uip-ds6.h"
#include "net/netstack.h"
#include "net/rpl/rpl.h"
#include "sensors/light-sensor.h"
#include "sensors/temperature-sensor.h"

#define PI 3.14159265358979323846

/* HTTP init */
// static const char *TOP
//     = "<html><head><title>ContikiRPL</title></head><body>\n";
// static const char *SCRIPT = "<script src=\"script.js\"></script>\n";
// static const char *BOTTOM = "</body></html>\n";
static char buf[512];
static int blen;
#define ADD(...)                                                   \
  do {                                                             \
    blen += snprintf(&buf[blen], sizeof(buf) - blen, __VA_ARGS__); \
  } while (0)

/* Init the environment. */
extern env myenv = {
  .day = 1,
  .hour = 0,
  .light = 0,
  .temperature_out = 28.0,
  .temperature_in = 28.0,
  .offset = 0.0,
  .lamp = {
    .state = 0,
  },
  .air_conditioner = {
    .state = 0,
  }
};

clock_time_t time_gap = CLOCK_SECOND;

inline void process_time() {
  int time_curr = myenv.hour + 1;
  if (time_curr == 24) {
    myenv.day += 1;
    time_curr = 0;
    srand(myenv.day * 24);
    myenv.offset = 6 * ((double)rand() / (double)RAND_MAX - 0.5);
  }
  myenv.hour = time_curr;
}

inline void process_daily_light() {
  int time_curr = myenv.hour;
  if (time_curr <= 6)
    myenv.light = 0;
  else if (time_curr <= 12)
    myenv.light = time_curr - 6;
  else if (time_curr <= 18)
    myenv.light = 18 - time_curr;
  else
    myenv.light = 0;
}

void process_temperature(double lower_bound, double upper_bound) {
  srand(myenv.day * 24 + myenv.hour);
  double mean = (lower_bound + upper_bound) / 2.0 + myenv.offset;
  double A = (upper_bound - lower_bound) / 2.0;
  double max_vibaration = A * (1 - sin(PI / 3));

  int time_curr = myenv.hour + 1;
  double curr_temp_mean = mean - A * sin(PI * (time_curr + 3) / 12.0);
  double vibration = max_vibaration * ((double)rand() / (double)RAND_MAX) - max_vibaration / 2;
  double curr_temp_out = curr_temp_mean + vibration;
  
  double prev_temp_out = myenv.temperature_out;
  // printf("prev_temp_out = %f\n", prev_temp_out);
  double prev_temp_in = myenv.temperature_in;
  // printf("prev_temp_in = %f\n", prev_temp_in);
  int ac_state = myenv.air_conditioner.state;
  double curr_temp_in = prev_temp_in + 5 * (ac_state == 2) - 3 * (ac_state == 1) + 0.4 * (prev_temp_out - prev_temp_in);
  // printf("curr_temp_in = %f\n", curr_temp_in);
  if (curr_temp_in > 35) {
    curr_temp_in = 35.0;
  } else if (curr_temp_in < 0) {
    curr_temp_in = 0.0;
  }

  myenv.temperature_out = curr_temp_out;
  myenv.temperature_in = curr_temp_in;
}

static void process_all() {
  process_time();
  process_daily_light();
  // if it is summer
  process_temperature(20.0, 36.0);
  // if it is winter
  // process_temperature(-10.0, 10.0);
}

PROCESS(simulation, "Simulation");
AUTOSTART_PROCESSES(&simulation);

// Main function
PROCESS_THREAD(simulation, ev, data) {
  PROCESS_BEGIN();
  static struct etimer timer;
  etimer_set(&timer, 3 * CLOCK_SECOND);

  httpd_init();
  while (1) {
    PROCESS_WAIT_EVENT();
    if (ev == PROCESS_EVENT_TIMER) {
      process_all();
      printf("Current time: %d, light intensity: %d, lamp state: %d\n",
             myenv.hour, get_light(), myenv.lamp.state);
      printf("Temperature outside: %.2f, Temperature inside: %.2f\n",
             myenv.temperature_out, get_temperature());
      printf("Air-conditioner state: %d\n", myenv.air_conditioner.state);
      etimer_restart(&timer);
    } else if (ev == tcpip_event)
      httpd_appcall(data);
  }
  PROCESS_END();
}

static PT_THREAD(generate_script(struct httpd_state *s)) {
  PSOCK_BEGIN(&s->sout);
  SEND_STRING(&s->sout,
              "\
  onload=function() {\
	p=location.host.replace(/::.*/,'::').substr(1);\
	a=document.getElementsByTagName('a');\
	for(i=0;i<a.length;i++) {\
		txt=a[i].innerHTML.replace(/^FE80::/,p);\
		a[i].href='http://['+txt+']';\
	}\
  }");
  PSOCK_END(&s->sout);
}

static PT_THREAD(generate_routes(struct httpd_state *s)) {
  static uip_ds6_route_t *r;
  static uip_ds6_nbr_t *nbr;

  static uip_ipaddr_t *preferred_parent_ip;
  rpl_dag_t *dag = rpl_get_any_dag();
  preferred_parent_ip = rpl_get_parent_ipaddr(dag->preferred_parent);

  // Start of the socket
  PSOCK_BEGIN(&s->sout);
  blen = 0;

  // Add sensor datas
  int light = get_light();
  int lamp_state = get_lamp_state();

  int ac_state = get_ac_state();
  double temp_in = get_temperature();
  double temp_out = myenv.temperature_out;

  // ADD adds the printline into the buffer buf
  ADD("{\"day\": %d, \"hour\": %d, \"light\": %d, \"lamp-state\": %d, "
      "\"ac-state\": %d, \"temperature-in\": %f, \"temperature-out\": %f}\n",
      myenv.day, myenv.hour, light, lamp_state, ac_state, temp_in, temp_out);
  // SEND_STRING will send the buffer, defined as the second parameter, to the
  // connected socket s, which is defined in the first parameter
  SEND_STRING(&s->sout, buf);
  // Reset the buffer line to 0
  blen = 0;

  PSOCK_END(&s->sout);
}

httpd_simple_script_t httpd_simple_get_script(const char *name) {
  if (!strcmp("script.js", name))
    return generate_script;
  else
    return generate_routes;
}