from unittest.mock import patch
from weather_tool import cli
import pytest
import io

@patch('weather_tool.cli.get_weather')
def test_main_with_city_and_default_unit(mock_get_weather):
    """Tests that main calls get_weather with the city and default Celsius unit."""
    with patch('sys.argv', ['weather', 'London']):
        cli.main()
    mock_get_weather.assert_called_once_with('London', 'C')

@patch('weather_tool.cli.get_weather')
def test_main_with_city_and_celsius(mock_get_weather):
    """Tests that main calls get_weather with the city and Celsius unit."""
    with patch('sys.argv', ['weather', 'London', '--unit', 'C']):
        cli.main()
    mock_get_weather.assert_called_once_with('London', 'C')

@patch('weather_tool.cli.get_weather')
def test_main_with_city_and_fahrenheit(mock_get_weather):
    """Tests that main calls get_weather with the city and Fahrenheit unit."""
    with patch('sys.argv', ['weather', 'London', '--unit', 'F']):
        cli.main()
    mock_get_weather.assert_called_once_with('London', 'F')

def test_main_no_city():
    """Tests that main exits and prints usage when no city is provided."""
    with patch('sys.argv', ['weather']):
        with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            with pytest.raises(SystemExit):
                cli.main()
            assert "usage:" in mock_stderr.getvalue()
