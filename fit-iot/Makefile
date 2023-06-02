CONTIKI_PROJECT = simulator
all: $(CONTIKI_PROJECT)

CONTIKI = ../iot-lab/parts/contiki

##############################
# HTTP Server
SMALL=1
CFLAGS += -DPROJECT_CONF_H=\"http-server-conf.h\"
PROJECT_SOURCEFILES += httpd-simple.c
CFLAGS += -DUIP_CONF_TCP=1
CFLAGS += -DWEBSERVER=1
ifeq ($(PREFIX),)
 PREFIX = aaaa::1/64
endif
CONTIKI_WITH_IPV6 = 1
##############################

include $(CONTIKI)/Makefile.include

