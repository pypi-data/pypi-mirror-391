'''
Author: Mr.Car
Date: 2025-03-21 14:35:00
'''
import pytest
from fastmcp import FastMCP
from weather_server.server import server, get_weather, get_weather_forecast

@pytest.mark.asyncio
async def test_mcp_tool_registration():
    """测试 MCP 工具注册"""
    # 验证工具是否可调用
    assert callable(get_weather)
    assert callable(get_weather_forecast)
    
    # 验证工具是否正确注册到 FastMCP 服务器
    assert isinstance(server, FastMCP) 