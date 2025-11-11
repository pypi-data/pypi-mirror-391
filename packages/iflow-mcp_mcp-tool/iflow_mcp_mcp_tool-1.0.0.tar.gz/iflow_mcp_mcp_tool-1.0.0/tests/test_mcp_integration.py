'''
Author: Mr.Car
Date: 2025-03-21 14:28:32
'''
import pytest
from weather_server.server import get_weather, get_weather_forecast
from weather_server.utils import CityNameConverter
from weather_server.models import WeatherData

@pytest.mark.asyncio
async def test_mcp_weather_call():
    """测试 MCP 天气服务调用"""
    # 测试实时天气工具调用
    result = await get_weather("suzhou")
    assert isinstance(result, WeatherData)
    assert result.description is not None
    assert isinstance(result.temperature, float)
    assert isinstance(result.humidity, int)
    assert isinstance(result.wind_speed, float)
    assert result.city == "suzhou"
    
    # 测试天气预报工具调用
    forecast = await get_weather_forecast("suzhou", days=1)
    assert isinstance(forecast, dict)
    assert 'forecasts' in forecast
    assert len(forecast['forecasts']) > 0
    assert all(isinstance(f['date'], str) for f in forecast['forecasts'])
    assert all(isinstance(f['description'], str) for f in forecast['forecasts'])
    assert all(isinstance(f['temp_min'], float) for f in forecast['forecasts'])
    assert all(isinstance(f['temp_max'], float) for f in forecast['forecasts'])
    assert all(isinstance(f['humidity'], int) for f in forecast['forecasts'])
    assert all(isinstance(f['wind_speed'], float) for f in forecast['forecasts'])

@pytest.mark.asyncio
async def test_mcp_chinese_city_name():
    """测试中文城市名称处理"""
    # 测试中文城市名
    result = await get_weather("苏州")
    assert isinstance(result, WeatherData)
    assert result.city == "苏州"
    
    # 测试天气预报中的中文城市名
    forecast = await get_weather_forecast("苏州", days=1)
    assert forecast['forecasts'][0]['city'] == "苏州"

@pytest.mark.asyncio
async def test_error_handling():
    """测试错误处理"""
    # 测试无效城市名
    with pytest.raises(Exception) as exc_info:
        await get_weather("invalid_city_name")
    assert "未找到城市" in str(exc_info.value)
    
    # 测试无效的天气预报请求
    with pytest.raises(Exception) as exc_info:
        await get_weather_forecast("invalid_city_name")
    assert "未找到城市" in str(exc_info.value)

def test_city_name_converter():
    """测试城市名称转换器"""
    converter = CityNameConverter()
    
    # 测试直接映射
    assert converter.to_english("苏州") == "suzhou"
    assert converter.to_english("北京") == "beijing"
    
    # 测试拼音转换
    assert converter.to_english("长沙") == "changsha"
    
    # 测试英文输入
    assert converter.to_english("Shanghai") == "shanghai"
    assert converter.to_english("BEIJING") == "beijing" 