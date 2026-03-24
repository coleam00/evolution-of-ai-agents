# Open-Meteo Weather API Reference

Open-Meteo is a free, open-source weather API that requires NO API key for non-commercial use.

## Base URL

```
https://api.open-meteo.com/v1/forecast
```

## Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `latitude` | Float | Yes | - | WGS84 coordinate (e.g., 40.71 for New York) |
| `longitude` | Float | Yes | - | WGS84 coordinate (negative for Americas, e.g., -74.01) |
| `current` | String | No | - | Comma-separated list of current weather variables |
| `hourly` | String | No | - | Comma-separated list of hourly forecast variables |
| `daily` | String | No | - | Comma-separated list of daily forecast variables |
| `temperature_unit` | String | No | celsius | Options: `celsius`, `fahrenheit` |
| `wind_speed_unit` | String | No | kmh | Options: `kmh`, `ms`, `mph`, `kn` |
| `precipitation_unit` | String | No | mm | Options: `mm`, `inch` |
| `timezone` | String | No | GMT | IANA timezone (e.g., `America/New_York`) |

## Current Weather Variables

Use with `current=` parameter:

| Variable | Unit | Description |
|----------|------|-------------|
| `temperature_2m` | C or F | Air temperature at 2 meters height |
| `relative_humidity_2m` | % | Relative humidity at 2 meters |
| `apparent_temperature` | C or F | Feels like temperature |
| `precipitation` | mm | Total precipitation |
| `rain` | mm | Rain amount |
| `showers` | mm | Shower amount |
| `snowfall` | cm | Snowfall amount |
| `weather_code` | WMO code | Weather condition code (see below) |
| `cloud_cover` | % | Total cloud cover |
| `pressure_msl` | hPa | Sea level pressure |
| `surface_pressure` | hPa | Surface pressure |
| `wind_speed_10m` | km/h | Wind speed at 10 meters |
| `wind_direction_10m` | degrees | Wind direction at 10 meters |
| `wind_gusts_10m` | km/h | Wind gusts at 10 meters |
| `is_day` | 0/1 | 1 if day, 0 if night |

## Weather Codes (WMO)

| Code | Description |
|------|-------------|
| 0 | Clear sky |
| 1 | Mainly clear |
| 2 | Partly cloudy |
| 3 | Overcast |
| 45 | Fog |
| 48 | Depositing rime fog |
| 51 | Light drizzle |
| 53 | Moderate drizzle |
| 55 | Dense drizzle |
| 56 | Light freezing drizzle |
| 57 | Dense freezing drizzle |
| 61 | Slight rain |
| 63 | Moderate rain |
| 65 | Heavy rain |
| 66 | Light freezing rain |
| 67 | Heavy freezing rain |
| 71 | Slight snow fall |
| 73 | Moderate snow fall |
| 75 | Heavy snow fall |
| 77 | Snow grains |
| 80 | Slight rain showers |
| 81 | Moderate rain showers |
| 82 | Violent rain showers |
| 85 | Slight snow showers |
| 86 | Heavy snow showers |
| 95 | Thunderstorm |
| 96 | Thunderstorm with slight hail |
| 99 | Thunderstorm with heavy hail |

## Example Requests

### Get Current Weather (Celsius)

```
https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.01&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m
```

### Get Current Weather (Fahrenheit)

```
https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.01&current=temperature_2m,weather_code,apparent_temperature&temperature_unit=fahrenheit
```

### Full Current Conditions

```
https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.01&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m&temperature_unit=fahrenheit&timezone=America/New_York
```

## Example Response

```json
{
  "latitude": 40.710335,
  "longitude": -73.99307,
  "generationtime_ms": 0.049,
  "utc_offset_seconds": -18000,
  "timezone": "America/New_York",
  "timezone_abbreviation": "EST",
  "elevation": 51.0,
  "current_units": {
    "time": "iso8601",
    "interval": "seconds",
    "temperature_2m": "F",
    "weather_code": "wmo code"
  },
  "current": {
    "time": "2024-01-15T14:00",
    "interval": 900,
    "temperature_2m": 42.5,
    "weather_code": 3
  }
}
```

## Error Handling

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 429 | Too many requests (rate limited) |

## Rate Limits

- Non-commercial: 10,000 requests/day
- No API key required for non-commercial use

## Tips

1. Always include `timezone` for accurate local times
2. Use `temperature_unit=fahrenheit` for US users
3. Combine multiple variables in one request to reduce API calls
4. Cache responses when possible (weather updates every 15 minutes)
