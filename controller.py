import pymysql
import urllib.request
import json
import time
import threading
from dataclasses import dataclass


class Controller:
    @dataclass(repr=True, eq=True, order=True)
    class Env:
        day: int
        hour: int
        light_intensity: int
        lamp_state: int
        temperature_out: float
        temperature_in: float
        air_conditioner_state: int

    @dataclass(repr=True)
    class EnableAutomation:
        lamp: bool = True
        air_conditioner: bool = True

    def __init__(self, ipv6_addr):
        self._connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            db='IoT-center'
        )
        self.ipv6_addr = ipv6_addr
        self._env = self.Env(0, 0, 0, 0, 0, 0, 0)
        self._enable_automation = self.EnableAutomation()
        self._collect_flag = True

    def get_env_parameters(self):
        url = f"http://[{self.ipv6_addr}]/"
        while self._collect_flag:
            req = urllib.request.Request(
                url,
                method='GET',
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response = urllib.request.urlopen(req, timeout=10)
            response = json.loads(response.read().decode())
            day = response['day']
            hour = response['hour']
            light_intensity = response['light']
            lamp_state = response['lamp-state']
            temperature_in = response['temperature-in']
            temperature_out = response['temperature-out']
            air_conditioner_state = response['ac-state']
            curr_env = self.Env(day, hour, light_intensity, lamp_state,
                                temperature_out, temperature_in, air_conditioner_state)
            print(curr_env)
            if self._env != curr_env:
                self._env = curr_env
                self._insert_env_param(curr_env)
                self._automation_control(curr_env)
            time.sleep(0.5)

    def _insert_env_param(self, env):
        try:
            with self._connection.cursor() as cursor:

                cursor.execute(
                    f"INSERT INTO env_param (day, hour, light_intensity, temperature_out, temperature_in)"
                    f" VALUES ({env.day}, {env.hour}, {env.light_intensity},"
                    f" {env.temperature_out}, {env.temperature_in})"
                )
                cursor.execute(
                    f"INSERT INTO devices (day, hour, lamp_state, lamp_automation, ac_state, ac_automation)"
                    f" VALUES ({env.day}, {env.hour}, {env.lamp_state}, {self._enable_automation.lamp},"
                    f" {env.air_conditioner_state}, {self._enable_automation.air_conditioner})"
                )
                self._connection.commit()
        except pymysql.err.IntegrityError as e:
            print(e)

    def _send_turn_on_lamp(self):
        url = f"http://[{self.ipv6_addr}]/?lamp=1"
        req = urllib.request.Request(
            url,
            method='GET',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=10)
        response = json.loads(response.read().decode())
        if response['lamp-state'] == 1:
            self._env.lamp_state = 1
            return True
        else:
            return False

    def _send_turn_off_lamp(self):
        url = f"http://[{self.ipv6_addr}]/?lamp=0"
        req = urllib.request.Request(
            url,
            method='GET',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=10)
        response = json.loads(response.read().decode())
        if response['lamp-state'] == 0:
            self._env.lamp_state = 0
            return True
        else:
            return False

    def _send_turn_off_air_conditioner(self):
        url = f"http://[{self.ipv6_addr}]/?ac=0"
        req = urllib.request.Request(
            url,
            method='GET',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=10)
        response = json.loads(response.read().decode())
        if response['ac-state'] == 0:
            self._env.air_conditioner_state = 0
            return True
        else:
            return False

    def _send_air_conditioner_cool(self):
        url = f"http://[{self.ipv6_addr}]/?ac=1"
        req = urllib.request.Request(
            url,
            method='GET',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=10)
        response = json.loads(response.read().decode())
        if response['ac-state'] == 1:
            self._env.air_conditioner_state = 1
            return True
        else:
            return False

    def _send_air_conditioner_heat(self):
        url = f"http://[{self.ipv6_addr}]/?ac=2"
        req = urllib.request.Request(
            url,
            method='GET',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=10)
        response = json.loads(response.read().decode())
        if response['ac-state'] == 2:
            self._env.air_conditioner_state = 2
            return True
        else:
            return False

    def turn_on_lamp(self):
        self._enable_automation.lamp = False
        return self._send_turn_on_lamp()

    def turn_off_lamp(self):
        self._enable_automation.lamp = False
        return self._send_turn_off_lamp()

    def turn_off_air_conditioner(self):
        self._enable_automation.air_conditioner = False
        return self._send_turn_off_air_conditioner()

    def air_conditioner_cool(self):
        self._enable_automation.air_conditioner = False
        return self._send_air_conditioner_cool()

    def air_conditioner_heat(self):
        self._enable_automation.air_conditioner = False
        return self._send_air_conditioner_heat()

    def _automation_control(self, curr_env):
        if self._enable_automation.lamp:
            if curr_env.light_intensity <= 1 and curr_env.lamp_state == 0:
                if self._send_turn_on_lamp():
                    print("\033[;34;mAutomatically turn on the lamp.\033[0m")
            elif curr_env.light_intensity > 1 and curr_env.lamp_state == 1:
                if self._send_turn_off_lamp():
                    print("\033[;34;mAutomatically turn off the lamp.\033[0m")
        if self._enable_automation.air_conditioner:
            if curr_env.temperature_in >= 30 and curr_env.air_conditioner_state != 1:
                if self._send_air_conditioner_cool():
                    print("\033[;34;mAutomatically turn on air conditioner to cooling mode.\033[0m")
            elif curr_env.temperature_in <= 10 and curr_env.air_conditioner_state != 2:
                if self._send_air_conditioner_heat():
                    print("\033[;34;mAutomatically turn on air conditioner to heating mode.\033[0m")
            elif 15 < curr_env.temperature_in < 25 and curr_env.air_conditioner_state != 0:
                if self._send_turn_off_air_conditioner():
                    print("\033[;34;mAutomatically turn off air conditioner.\033[0m")

    def cli(self):
        get_env_param_thread = None
        while True:
            command = input("\033[;32;m> \033[0m")

            ####### Automation #######
            if command == "turn on lamp automation":
                self._enable_automation.lamp = True
            elif command == "turn off lamp automation":
                self._enable_automation.lamp = False
            elif command == "turn on air conditioner automation":
                self._enable_automation.air_conditioner = True
            elif command == "turn off air conditioner automation":
                self._enable_automation.air_conditioner = False
            elif command == "check automation":
                for key, value in self._enable_automation.__dict__.items():
                    print(f"{key}: {value}")

            ####### Manual Control #######
            elif command == "turn on lamp":
                res = self.turn_on_lamp()
                if res:
                    print("\033[;32;mSuccess.\033[0m")
                else:
                    print("\033[;31;mFailed.\033[0m")

            elif command == "turn off lamp":
                res = self.turn_off_lamp()
                if res:
                    print("\033[;32;mSuccess.\033[0m")
                else:
                    print("\033[;31;mFailed.\033[0m")

            elif command == "turn off air conditioner":
                res = self.turn_off_air_conditioner()
                if res:
                    print("\033[;32;mSuccess.\033[0m")
                else:
                    print("\033[;31;mFailed.\033[0m")

            elif command == "air conditioner cool":
                res = self.air_conditioner_cool()
                if res:
                    print("\033[;32;mSuccess.\033[0m")
                else:
                    print("\033[;31;mFailed.\033[0m")

            elif command == "air conditioner heat":
                res = self.air_conditioner_heat()
                if res:
                    print("\033[;32;mSuccess.\033[0m")
                else:
                    print("\033[;31;mFailed.\033[0m")

            ####### Server #######
            elif command == "server start":
                get_env_param_thread = threading.Thread(target=self.get_env_parameters)
                get_env_param_thread.start()
                if get_env_param_thread.is_alive():
                    print("\033[;32;mServer started.\033[0m")

            elif command == "server stop":
                self._collect_flag = False
                if get_env_param_thread is not None:
                    get_env_param_thread.join()
                    print("\033[;32;mServer stopped.\033[0m")
                else:
                    print("\033[;31;mServer is not running.\033[0m")

            elif command.startswith("show env parameters"):
                if command.split(" ")[-2] == '-t':
                    show_time = int(command.split(" ")[-1])
                    while show_time:
                        show_time -= 1
                        print(self._env)
                        time.sleep(1)
                else:
                    print(self._env)

            elif command == "exit":
                self._collect_flag = False
                break


def main():
    controller = Controller('2001:660:5307:3111::a777')
    controller.cli()


if __name__ == '__main__':
    main()
