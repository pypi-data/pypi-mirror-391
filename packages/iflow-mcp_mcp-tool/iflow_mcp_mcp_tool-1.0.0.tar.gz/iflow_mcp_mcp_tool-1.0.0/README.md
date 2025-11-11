<!--
 * @Author: Mr.Car
 * @Date: 2025-03-20 17:40:04
-->
<div align="center">
  <img src="https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3MjU5MDl8MHwxfHNlYXJjaHwxfHxiZWF1dGlmdWwlMjB3ZWF0aGVyJTIwbGFuZHNjYXBlfGVufDB8fHx8MTc0MjU0NzkxN3ww&ixlib=rb-4.0.3&q=80&w=1080" alt="Weather MCP Tool" width="100%">
  <h1>Weather MCP Tool</h1>
  <p>A minimalist weather query tool that lets you check global weather with just one sentence, perfectly integrated with Cursor editor.</p>
  
  [![smithery badge](https://smithery.ai/badge/@MrCare/mcp_tool)](https://smithery.ai/server/@MrCare/mcp_tool)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
  
  [English](README.md) | [中文](README_zh.md)
</div>

<div align="center">
  <img src="real_en.gif" alt="Weather MCP Tool Demo" width="100%">
  <p><i>Watch how easy it is to query weather with natural language</i></p>
</div>

## ✨ Features

- 💡 **Minimalist**: One-line weather query
- 🤖 **Smart**: Natural language support in Chinese/English
- 🌏 **Global**: Support for all major cities
- 🔌 **Plug & Play**: Perfect Cursor integration
- 🚀 **High Performance**: Async processing, quick response
- 🎨 **Beautiful**: Clear and intuitive weather display

## 🚀 Quick Start

### 1. Get API Key

> 🔑 Before starting, please [Get OpenWeather API Key](https://home.openweathermap.org/api_keys)

### 2. One-Click Installation (Recommended)

Install and configure with Smithery in one command:

```bash
npx -y @smithery/cli@latest install @MrCare/mcp_tool --client cursor --config "{\"openweathermapApiKey\":\"your_api_key_here\",\"port\":8000}"
```

> For WindSurf and Cine installation, please visit our [Smithery repository](https://smithery.ai/server/@MrCare/mcp_tool).

### 3. Manual Installation

#### 3.1 Clone and Install

```bash
git clone https://github.com/yourusername/weather-server.git && cd weather-server && pip install -e .
```

#### 3.2 Configure API Key

**Method 1: Using Configuration File (Recommended)**

Copy the example configuration file and modify it:
```bash
cp env.example .env
```
Then edit the `.env` file, replace `your_api_key_here` with your API Key.

**Method 2: Using Environment Variables**

macOS/Linux:
```bash
export OPENWEATHERMAP_API_KEY="your_api_key"
```

Windows:
```cmd
set OPENWEATHERMAP_API_KEY=your_api_key
```

#### 3.3 Enable Tool

Edit `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`):
```json
{
    "weather_fastmcp": {
        "command": "python",
        "args": ["-m", "weather_server.server"]
    }
}
```

Restart Cursor and you're ready to go!

## 📝 Usage Examples

Simply type in Cursor:
```
Show me the weather in Tokyo
What's the forecast for London?
How's the weather in New York?
Will it rain tomorrow in Paris?
```

That's it!

## ⚙️ Parameters

For more precise queries, you can specify these parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| city | City name (Chinese/English) | Required |
| days | Forecast days (1-5) | 5 |
| units | Temperature unit (metric: Celsius, imperial: Fahrenheit) | metric |
| lang | Response language (zh_cn: Chinese, en: English) | zh_cn |

## ❓ FAQ

1. **Not Working?**
   - Ensure API Key is set correctly
   - Restart Cursor
   - Check Python environment

2. **City Not Found?**
   - Try using English name
   - Check spelling
   - Use complete city name

## 👨‍💻 Author

- Mr.Car
- Email: 534192336car@gmail.com

## 🙏 Acknowledgments

- [FastMCP](https://github.com/microsoft/fastmcp)
- [OpenWeatherMap](https://openweathermap.org/)
- [Cursor](https://cursor.sh/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
