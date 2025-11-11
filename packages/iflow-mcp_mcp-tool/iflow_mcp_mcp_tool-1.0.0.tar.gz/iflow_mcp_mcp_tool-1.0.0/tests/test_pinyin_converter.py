'''
Author: Mr.Car
Date: 2025-03-21 14:29:41
'''
import pytest
from weather_server.server import CityNameConverter

def test_pinyin_conversion():
    """测试拼音转换功能"""
    converter = CityNameConverter()
    
    # 测试基本映射
    assert converter.to_english("苏州") == "suzhou"
    assert converter.to_english("北京") == "beijing"
    assert converter.to_english("上海") == "shanghai"
    
    # 测试未知城市的拼音转换
    assert converter.to_english("杭州") == "hangzhou"
    assert converter.to_english("南京") == "nanjing"
    
    # 测试英文输入
    assert converter.to_english("suzhou") == "suzhou"
    assert converter.to_english("BEIJING") == "beijing"
    
    # 测试特殊情况
    assert converter.to_english("") == ""
    assert converter.to_english("123") == "123"

def test_city_map_coverage():
    """测试城市映射表覆盖情况"""
    converter = CityNameConverter()
    
    # 验证所有预定义的城市映射
    predefined_cities = {
        "苏州": "suzhou",
        "北京": "beijing",
        "上海": "shanghai",
        "广州": "guangzhou",
        "深圳": "shenzhen"
    }
    
    for cn_city, en_city in predefined_cities.items():
        assert converter.to_english(cn_city) == en_city

def test_pinyin_edge_cases():
    """测试拼音转换的边界情况"""
    converter = CityNameConverter()
    
    # 测试混合中英文
    assert converter.to_english("苏州city") == "suzhoucity"
    
    # 测试特殊字符
    assert converter.to_english("苏州市") == "suzhoushi"
    assert converter.to_english("长春-市") == "changchunshi" 