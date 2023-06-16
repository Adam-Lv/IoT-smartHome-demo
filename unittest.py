import pymysql

from model import Model
connection = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='root',
    db='IoT-center'
)

model = Model()
print(model.select_temperature_in(connection).__len__())
print(model.select_temperature_out(connection))
print(model.select_light_intensity(connection))
print(model.get_daily_air_conditioner_using_time(connection))
acut = model.get_daily_air_conditioner_using_time(connection)
print(type(acut[0][1]), int(acut[0][1]))

print(model.get_avg_temp_out(connection))
