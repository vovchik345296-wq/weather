cat > main.py << 'EOF'
import certifi
from urllib.parse import quote
from kivy.app import App
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import StringProperty

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 10
    TextInput:
        id: city
        text: 'Москва'
        hint_text: 'Город'
        multiline: False
        size_hint_y: None
        height: 60
        font_size: 22
    Button:
        text: 'Узнать погоду'
        size_hint_y: None
        height: 70
        font_size: 20
        on_release: app.search(city.text)
    Label:
        text: app.result
        font_size: 20
        halign: 'center'
        valign: 'top'
        text_size: self.width, self.height
'''

CODES = {0: 'Ясно', 1: 'Малооблачно', 2: 'Облачно', 3: 'Пасмурно',
         45: 'Туман', 48: 'Туман', 51: 'Морось', 53: 'Морось', 55: 'Морось',
         61: 'Дождь', 63: 'Дождь', 65: 'Сильный дождь',
         71: 'Снег', 73: 'Снег', 75: 'Сильный снег',
         80: 'Ливень', 81: 'Ливень', 82: 'Сильный ливень',
         95: 'Гроза', 96: 'Гроза с градом', 99: 'Гроза с градом'}

class WeatherApp(App):
    result = StringProperty('Введите город')

    def build(self):
        self.title = 'Weather'
        return Builder.load_string(KV)

    def search(self, city):
        city = city.strip()
        if not city:
            return
        self.result = 'Загрузка...'
        url = ('https://geocoding-api.open-meteo.com/v1/search?name='
               + quote(city) + '&count=1&language=ru')
        UrlRequest(url, on_success=self.got_city, on_failure=self.fail,
                   on_error=self.fail, ca_file=certifi.where())

    def got_city(self, req, data):
        res = data.get('results')
        if not res:
            self.result = 'Город не найден'
            return
        p = res[0]
        self.name = p['name']
        url = ('https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s'
               '&current=temperature_2m,apparent_temperature,relative_humidity_2m,'
               'wind_speed_10m,weather_code'
               '&daily=temperature_2m_max,temperature_2m_min'
               '&timezone=auto&forecast_days=3') % (p['latitude'], p['longitude'])
        UrlRequest(url, on_success=self.got_weather, on_failure=self.fail,
                   on_error=self.fail, ca_file=certifi.where())

    def got_weather(self, req, data):
        c = data['current']
        d = data['daily']
        text = '%s\n\n%+.0f°C (ощущается %+.0f°C)\n%s\nВлажность: %s%%\nВетер: %s км/ч\n\nПрогноз:\n' % (
            self.name, c['temperature_2m'], c['apparent_temperature'],
            CODES.get(c['weather_code'], '—'),
            c['relative_humidity_2m'], c['wind_speed_10m'])
        for i in range(3):
            text += '%s: %+.0f / %+.0f°C\n' % (
                d['time'][i][5:], d['temperature_2m_min'][i], d['temperature_2m_max'][i])
        self.result = text

    def fail(self, req, err):
        self.result = 'Ошибка сети. Проверьте интернет.'

WeatherApp().run()
EOF
