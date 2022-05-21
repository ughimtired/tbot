import SECRET  # секретные ключи, пароли

def get_wind_direction(deg, advanced_result=False):
    l = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
    l_adv = ['Северный', 'Северо-Восточный', 'Восточный', 'Юго-Восточный', 'Южный', 'Юго-Западный', 'Западный', 'Северо-Западный']
    for i in range(0, 8):
        step = 45.
        min = i * step - 45 / 2.
        max = i * step + 45 / 2.
        if i == 0 and deg > 360 - 45 / 2.:
            deg = deg - 360
        if deg >= min and deg <= max:
            res = l_adv[i] if advanced_result else l[i]
            break
    return res


class OpenWeatherMap():
    # для получения своего бесплатного ключа пройдите регистрацию: https://home.openweathermap.org/users/sign_up

    def __init__(self):
        pass


    # # Проверка наличия в базе информации о нужном населенном пункте
    # def getAPI_cityID(self, s_city_name, type='like', units='metric', lang='ru'):
    #     import requests
    #     try:
    #         res = requests.get("http://api.openweathermap.org/data/2.5/find",
    #                            params={'q': s_city_name, 'type': type, 'units': units, 'lang': lang,
    #                                    'APPID': SECRET.OWM_TOKEN})
    #         data = res.json()
    #         cities = ["{} ({})".format(d['name'], d['sys']['country'])
    #                   for d in data['list']]
    #         print("city:", cities)
    #         city_id = data['list'][0]['id']
    #         print('city_id=', city_id)
    #     except Exception as e:
    #         print("Exception (find):", e)
    #         pass
    #     assert isinstance(city_id, int)
    #     return city_id

    # Запрос текущей погоды
    def getAPI_requestCurrentWeather(self, city_id, units='metric', lang='ru'):
        import requests
        text = ""
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': city_id, 'units': units, 'lang': lang, 'APPID': SECRET.OWM_TOKEN})
        if res.status_code == 200:
            data = res.json()
            text += f"Погода для: {data['name']}(id:{data['id']}) координаты: N{data['coord']['lat']}, E{data['coord']['lon']} Яндекс: https://yandex.ru/maps/?ll={data['coord']['lon']},{data['coord']['lat']}&z=12&l=map\n"
            text += f"Погодная обстановка: {data['weather'][0]['description']}\n"
            text += f"Температура: {data['main']['temp']}  ощущается {data['main']['feels_like']} (min: {data['main']['temp_min']}, max: {data['main']['temp_max']})\n"
            text += f"Давление: {data['main']['pressure']}мм, Влажность: {data['main']['humidity']}%\n"
            text += f"Ветер: {get_wind_direction(data['wind']['deg'])}, {data['wind']['speed']}м/с\n"
            # text += "data: " + str(data)
        else:
            text = res.text

        return text

    # запрос координат
    def getAPI_geocoding(self, lat, lon, limit=1, lang='ru'):
        import requests
        text = ""
        res = requests.get("http://api.openweathermap.org/geo/1.0/reverse",
                           params={'lat': lat, 'lon': lon, 'limit': limit, 'APPID': SECRET.OWM_TOKEN})
        if res.status_code == 200:
            data = res.json()
            for var in data:
                text += f"{var['local_names'][lang]} ({var['country']}) координаты: N{var['lat']}, E{var['lon']} Яндекс: https://yandex.ru/maps/?ll={var['lon']},{var['lat']}&z=12&l=map\n"
            # text += "data: " + str(data)
        else:
            text = res.text
        return text

    # # Прогноз
    # def getAPI_requestForecast(self, city_id, units='metric', lang='ru'):
    #     import requests
    #     try:
    #         res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
    #                            params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': SECRET.OWM_TOKEN})
    #         data = res.json()
    #         print('city:', data['city']['name'], data['city']['country'])
    #         for i in data['list']:
    #             print((i['dt_txt'])[:16], '{0:+3.0f}'.format(i['main']['temp']),
    #                   '{0:2.0f}'.format(i['wind']['speed']) + " м/с",
    #                   get_wind_direction(i['wind']['deg']),
    #                   i['weather'][0]['description'])
    #     except Exception as e:
    #         print("Exception (forecast):", e)
    #         pass

class WeatherFromPyOWN:
    # для получения своего бесплатного ключа пройдите регистрацию: https://home.openweathermap.org/users/sign_up

    def __init__(self):
        pass


    def getWeatherAtCoords(self, lat, lon):
        text = ""
        try:
            from pyowm import OWM
            from pyowm.utils import config
            from pyowm.utils import timestamps

            config_dict = config.get_default_config()
            config_dict['language'] = 'ru'

            owm = OWM(SECRET.OWM_TOKEN, config_dict)
            mgr = owm.weather_manager()

            result = mgr.weather_at_coords(lat, lon)
            l = result.location
            w = result.weather
            t = w.temperature('celsius')
            wind = w.wind()

            text += f"Погода для: {l.name}(id:{l.id}) координаты: N{l.lat}, E{l.lon} Яндекс: https://yandex.ru/maps/?ll={l.lon},{l.lat}&z=12&l=map\n"
            text += f"\tПогодная обстановка: {w.detailed_status}\n"
            text += f"\tТемпература: {t['temp']}C  ощущается {t['feels_like']} (min: {t['temp_min']}, max: {t['temp_max']})\n"
            text += f"\tДавление: {w.pressure['press']}мм, Влажность: {w.humidity}%\n"
            text += f"\tВетер: {get_wind_direction(wind['deg'], True)}, {wind['speed']}м/с\n"
            if len(w.rain) == 0 and len(w.snow) == 0:
                text += f"\tОсадков нет\n"
            elif len(w.rain) > 0:
                text += f"\t\tЗа последний час {w.rain['1h']}мм дождя\n"
            elif len(w.snow) > 0:
                text += f"\t\tЗа последний час {w.snow['1h']}мм снега\n"

        except Exception as e:
            text = f"Exception (forecast): {e}"

        return text

    def getWeatherForecastAtCoords(self, lat, lon):
        text = ""
        try:
            from pyowm import OWM
            from pyowm.utils import config
            from pyowm.utils import timestamps

            config_dict = config.get_default_config()
            config_dict['language'] = 'ru'

            owm = OWM(SECRET.OWM_TOKEN, config_dict)
            mgr = owm.weather_manager()
            tomorrow = timestamps.tomorrow()
            Forecast = mgr.forecast_at_coords(lat, lon, '3h')
            w = Forecast.get_weather_at(tomorrow)
            t = w.temperature('celsius')
            wind = w.wind()

            text += f"Прогноз на {str(tomorrow.date())}: {w.detailed_status}\n"
            text += f"\tТемпература: {t['temp']}C  ощущается {t['feels_like']} (min: {t['temp_min']}, max: {t['temp_max']})\n"
            text += f"\tДавление: {w.pressure['press']}мм, Влажность: {w.humidity}%\n"
            text += f"\tВетер: {get_wind_direction(wind['deg'], True)}, {wind['speed']}м/с\n"
            # if len(w.rain) == 0 and len(w.snow) == 0:
            #     text += f"Осадков нет\n"
            # elif len(w.rain) > 0:
            #     text += f"За последний час {w.rain['1h']}мм дождя\n"
            # elif len(w.snow) > 0:
            #     text += f"За последний час {w.snow['1h']}мм снега\n"


        except Exception as e:
            text = f"Exception (forecast): {e}"

        return text

# owm = OpenWeatherMap()
# print(owm.getAPI_requestCurrentWeather("519690"))  # city_id for SPb
# print(owm.getAPI_geocoding(59.858390, 30.398006, 10))

# pyOWN = WeatherFromPyOWN()
# print(pyOWN.getWeatherAtCoords(59.858390, 30.398006))
# print(pyOWN.getWeatherForecastAtCoords(59.858390, 30.398006))