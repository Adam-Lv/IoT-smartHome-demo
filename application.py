import threading

import pymysql
from flask import Flask, request
from controller import Controller
from model import Model
import json
import yaml
import datetime

with open("config.yml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

app = Flask(
    __name__,
    static_folder=config["back_end"]["static_folder"],
    static_url_path="",
    root_path=""
)
day0 = datetime.datetime(2023, 6, 1)


def create_connection():
    return pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root',
        db='IoT-center'
    )


controller = Controller(config["back_end"]["remote_ipv6"])
model = Model()


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return app.send_static_file('assets/favicon.svg')


@app.route('/')
def index():
    return app.send_static_file('index.html')


def get_temperature_in():
    connection = create_connection()
    sql_res = model.select_temperature_in(connection)
    temps = [round(row[1], 1) for row in sql_res]
    day = (day0 + datetime.timedelta(days=sql_res[0][0])).strftime('%Y-%m-%d')
    connection.close()
    return json.dumps({
        "day": day,
        "temps": temps
    })


def get_temperature_out():
    connection = create_connection()
    sql_res = model.select_temperature_out(connection)
    temps = [round(row[1], 1) for row in sql_res]
    day = (day0 + datetime.timedelta(days=sql_res[0][0])).strftime('%Y-%m-%d')
    connection.close()
    return json.dumps({
        "day": day,
        "temps": temps
    })


def get_light_intensity():
    connection = create_connection()
    sql_res = model.select_light_intensity(connection)
    day = (day0 + datetime.timedelta(days=sql_res[0][0])).strftime('%Y-%m-%d')
    lights = [row[1] for row in sql_res]
    connection.close()
    return json.dumps({
        "day": day,
        "lights": lights
    })


def air_conditioner_usage_time():
    connection = create_connection()
    sql_res = model.get_daily_air_conditioner_using_time(connection)
    day_labels = [(day0 + datetime.timedelta(days=row[0])).strftime('%Y-%m-%d') for row in sql_res]
    using_times = [int(row[1]) for row in sql_res]
    connection.close()
    return json.dumps({
        "day_labels": day_labels,
        "using_times": using_times
    })


def avg_temp_out():
    connection = create_connection()
    sql_res = model.get_avg_temp_out(connection)
    day_labels = [(day0 + datetime.timedelta(days=row[0])).strftime('%Y-%m-%d') for row in sql_res]
    avg_temps = [round(row[1], 1) for row in sql_res]
    connection.close()
    return json.dumps({
        "day_labels": day_labels,
        "avg_temps": avg_temps
    })


@app.route('/api/data-fetch', methods=['POST'])
def data_fetch():
    data_type = request.form.get('data_type')
    # print(data_type)
    if data_type == 'temperature_in':
        return get_temperature_in()
    elif data_type == 'temperature_out':
        return get_temperature_out()
    elif data_type == 'light_intensity':
        return get_light_intensity()
    elif data_type == 'air_conditioner_usage_time':
        return air_conditioner_usage_time()
    elif data_type == 'avg_temp_out':
        return avg_temp_out()


@app.route('/api/device-control', methods=['POST'])
def device_control():
    device = request.form.get('device')
    state = int(request.form.get('state'))
    automation = int(request.form.get('automation'))
    res = None
    print(device, state, automation)
    if device == 'lamp':
        try:
            if state == 1:
                res = controller.turn_on_lamp()
            elif state == 0:
                res = controller.turn_off_lamp()
            else:
                if automation != -1:
                    controller._enable_automation.lamp = bool(automation)
                    res = True
        except Exception as e:
            print(e)
    elif device == 'ac':
        try:
            if state == 1:
                res = controller.air_conditioner_cool()
            elif state == 2:
                res = controller.air_conditioner_heat()
            elif state == 0:
                res = controller.turn_off_air_conditioner()
            else:
                if automation != -1:
                    controller._enable_automation.air_conditioner = bool(automation)
                    res = True
        except Exception as e:
            print(e)
    if res:
        print(res)
        return json.dumps({'code': 0})
    else:
        print(res)
        return json.dumps({'code': 1})


@app.route('/api/device-info', methods=['POST'])
def device_info():
    res = {
        'lamp': [controller._env.lamp_state, int(controller._enable_automation.lamp)],
        'ac': [controller._env.air_conditioner_state, int(controller._enable_automation.air_conditioner)]
    }
    return json.dumps(res)


if __name__ == '__main__':
    # get_env_param_thread = threading.Thread(target=controller.get_env_parameters)
    # get_env_param_thread.start()
    app.run(port=config['back_end']['port'])
