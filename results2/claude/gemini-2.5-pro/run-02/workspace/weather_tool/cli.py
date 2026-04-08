#!/usr/bin/env python3
import sys
import argparse
import urllib.request
import urllib.error
import urllib.parse
import json
import os
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".weather_cache"
CACHE_EXPIRATION = 15 * 60  # 15 minutes

def get_weather(city, unit="C", short=False, no_cache=False):
    """Fetches and displays weather from wttr.in, using a cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    city_slug = urllib.parse.quote(city.lower())
    cache_file_ext = ".short.txt" if short else ".txt"
    cache_file = CACHE_DIR / f"{city_slug}_{unit.lower()}{cache_file_ext}"

    if not no_cache and cache_file.exists() and (time.time() - cache_file.stat().st_mtime) < CACHE_EXPIRATION:
        return True, cache_file.read_text()

    unit_param = "?m" if unit.upper() == 'C' else "?u"
    city_encoded = urllib.parse.quote(city)
    format_param = "&format=%l:+%c+%t" if short else ""
    url = f'http://wttr.in/{city_encoded}{unit_param}{format_param}'

    try:
        # First, validate the city with the JSON API
        validation_url = f'http://wttr.in/{city_encoded}?format=j1'
        req = urllib.request.Request(validation_url, headers={'User-Agent': 'curl'})
        with urllib.request.urlopen(req) as response:
            weather_data = json.load(response)
            found_city = False
            query_city = city.lower()
            for area in weather_data.get('nearest_area', []):
                for field in ['areaName', 'region', 'country']:
                    if any(query_city in value['value'].lower() for value in area.get(field, [])):
                        found_city = True
                        break
                if found_city:
                    break
            if not found_city:
                return False, f"Could not find weather for city '{city}'"

        # If validated, fetch the actual report
        req = urllib.request.Request(url, headers={'User-Agent': 'curl'})
        with urllib.request.urlopen(req) as response:
            weather_report = response.read().decode('utf-8')
            if not no_cache:
                cache_file.write_text(weather_report)
            return True, weather_report

    except urllib.error.HTTPError as e:
        return False, f"Error fetching weather: {e.code} {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Error: Could not connect to the weather service. {e.reason}"

def main():
    """Parses arguments and calls get_weather."""
    parser = argparse.ArgumentParser(description="Get the weather for a city.")
    parser.add_argument("city", nargs='+', help="The city to get the weather for.")
    parser.add_argument("-u", "--unit", choices=['C', 'F'], default='C', help="Temperature unit (C for Celsius, F for Fahrenheit)")
    parser.add_argument("-s", "--short", action="store_true", help="Display a short, one-line weather report.")
    parser.add_argument("--no-cache", action="store_true", help="Bypass the cache.")
    args = parser.parse_args()
    city_name = ' '.join(args.city)
    success, output = get_weather(city_name, args.unit, args.short, args.no_cache)
    if success:
        print(output)
    else:
        print(output, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
