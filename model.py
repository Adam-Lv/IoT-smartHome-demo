class Model:
    @staticmethod
    def select_temperature_in(connection):
        select = """
        SELECT
            day, temperature_in
        FROM
            env_param
        WHERE
            day = (SELECT MAX(day) FROM env_param)
        """
        with connection.cursor() as cursor:
            cursor.execute(select)
            result = cursor.fetchall()
            return result

    @staticmethod
    def select_temperature_out(connection):
        select = """
        SELECT
            day, temperature_out
        FROM
            env_param
        WHERE
            day = (SELECT MAX(day) FROM env_param)
        """
        with connection.cursor() as cursor:
            cursor.execute(select)
            result = cursor.fetchall()
            return result

    @staticmethod
    def select_light_intensity(connection):
        select = """
        SELECT 
            day, light_intensity
        FROM
            env_param
        WHERE 
            day = (SELECT MAX(day) FROM env_param)
        """
        with connection.cursor() as cursor:
            cursor.execute(select)
            result = cursor.fetchall()
            return result

    @staticmethod
    def get_daily_air_conditioner_using_time(connection):
        select = """
        SELECT 
          day, 
          SUM(ac_state * 1) AS ac_using_time
        FROM 
          devices 
        WHERE 
          day >= (SELECT MAX(day) - 6 FROM devices) AND day < (SELECT MAX(day) FROM devices) AND ac_state = 1
        GROUP BY 
          day
        """
        with connection.cursor() as cursor:
            cursor.execute(select)
            result = cursor.fetchall()
            return result

    @staticmethod
    def get_avg_temp_out(connection):
        select = """
        SELECT
            day, AVG(temperature_out) AS avg_temp_out
        FROM
            env_param
        WHERE
            day >= (SELECT MAX(day) - 6 FROM env_param) AND day < (SELECT MAX(day) FROM env_param)
        GROUP BY
            day
        """
        with connection.cursor() as cursor:
            cursor.execute(select)
            result = cursor.fetchall()
            return result
