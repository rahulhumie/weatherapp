import requests
from django.shortcuts import render
from .forms import CityForm
from django.core.cache import cache

API_KEY = 'a0f63ddfc82b50ab61889f00497afbcd'

def get_weather_data(city):
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    weather_response = requests.get(weather_url)
    weather_json = weather_response.json()

    lat = weather_json['coord']['lat']
    lon = weather_json['coord']['lon']
    pollution_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}'
    pollution_response = requests.get(pollution_url)
    pollution_json = pollution_response.json()

    return {
        'temperature': weather_json['main']['temp'],
        'rain': weather_json['weather'][0]['main'],
        'pollution': pollution_json['list'][0]['main']['aqi'],
    }

def get_weather(request):
    weather_data = None
    form = CityForm()

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']

            # Check cache first
            cache_key = f"weather_{city}"
            weather_data = cache.get(cache_key)

            if not weather_data:
                weather_data = get_weather_data(city)
                cache.set(cache_key, weather_data, timeout=3600)  # Cache for 1 hour

    return render(request, 'weather/weather.html', {'form': form, 'weather_data': weather_data})
