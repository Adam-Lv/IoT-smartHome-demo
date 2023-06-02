# sudo tunslip6.py -v2 -L -a m3-322 -p 20000 2001:660:5307:3111::1/64
# iotlab-node --flash border-router.iotlab-m3 -l grenoble,m3,322
# iotlab-node --flash simulator.iotlab-m3 -l grenoble,m3,323
lynx -dump http://[2001:660:5307:3111::b282]
lynx -dump http://[2001:660:5307:3111::a777]