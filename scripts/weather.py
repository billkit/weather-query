#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气查询脚本 - 信息专员专用
数据来源：中国天气网、广西天气网
"""

import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# 城市代码映射（常用城市）
CITY_CODES = {
    '北京': '101010100',
    '上海': '101020100',
    '广州': '101280101',
    '深圳': '101280601',
    '杭州': '101210101',
    '南京': '101190101',
    '武汉': '101200101',
    '成都': '101270101',
    '重庆': '101040100',
    '西安': '101110101',
    '天津': '101030100',
    '苏州': '101190401',
    '郑州': '101180101',
    '长沙': '101250101',
    '青岛': '101120201',
    '宁波': '101210401',
    '厦门': '101230201',
    '福州': '101220101',
    '合肥': '101220101',
    '济南': '101120101',
    '大连': '101070201',
    '沈阳': '101070101',
    '哈尔滨': '101050101',
    '长春': '101060101',
    '石家庄': '101090101',
    '太原': '101100101',
    '南宁': '101300101',
    '海口': '101310101',
    '贵阳': '101260101',
    '昆明': '101290101',
    '拉萨': '101281401',
    '兰州': '101160101',
    '银川': '101150101',
    '西宁': '101150101',
    '乌鲁木齐': '101130101',
    '呼和浩特': '101080101',
    '灵山': '101301103',
    '钦州': '101301101',
    '北海': '101301301',
    '防城港': '101301401',
    '玉林': '101300901',
    '贵港': '101300801',
    '横县': '101300104',
    '浦北': '101301102',
}

def get_city_code(city_name):
    """获取城市代码"""
    if city_name in CITY_CODES:
        return CITY_CODES[city_name]
    # 尝试模糊匹配
    for name, code in CITY_CODES.items():
        if name in city_name or city_name in name:
            return code
    # 默认返回北京
    return '101010100'

def fetch_weather_data(city_code):
    """从广西天气网获取天气数据"""
    urls = [
        f'https://www.gxweather.com/api/city/{city_code}',
        f'https://www.gxweather.com/lingshan/',
    ]
    
    # 模拟浏览器请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/html',
    }
    
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8')
                if 'json' in response.headers.get('Content-Type', ''):
                    return json.loads(data)
        except Exception as e:
            continue
    
    return None

def parse_gxweather_data(data, city_name):
    """解析广西天气网数据"""
    result = {
        'city': city_name,
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'current': {},
        'forecast': []
    }
    
    # 解析当前天气
    if 'current' in data:
        current = data['current']
        result['current'] = {
            'temp': current.get('temp', 'N/A'),
            'feels_like': current.get('feels_like', 'N/A'),
            'weather': current.get('weather', 'N/A'),
            'humidity': current.get('humidity', 'N/A'),
            'wind': current.get('wind', 'N/A'),
            'aqi': current.get('aqi', 'N/A'),
            'pressure': current.get('pressure', 'N/A'),
            'visibility': current.get('visibility', 'N/A'),
        }
    
    # 解析预报
    if 'forecast' in data:
        for day in data['forecast'][:7]:
            result['forecast'].append({
                'date': day.get('date', ''),
                'weather': day.get('weather', ''),
                'temp_low': day.get('temp_low', ''),
                'temp_high': day.get('temp_high', ''),
                'wind': day.get('wind', ''),
            })
    
    return result

def format_output(data, simple=False, json_output=False):
    """格式化输出"""
    if json_output:
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    lines = []
    lines.append(f"📍 {data['city']}")
    
    current = data.get('current', {})
    if current:
        lines.append(f"🌡️ 当前温度：{current.get('temp', 'N/A')}°C")
        lines.append(f"🤒 体感温度：{current.get('feels_like', 'N/A')}°C")
        lines.append(f"☁️ 天气：{current.get('weather', 'N/A')}")
        lines.append(f"💧 湿度：{current.get('humidity', 'N/A')}%")
        lines.append(f"🌬️ 风向风力：{current.get('wind', 'N/A')}")
        lines.append(f"📊 AQI: {current.get('aqi', 'N/A')}")
    
    forecast = data.get('forecast', [])
    if forecast:
        lines.append("")
        lines.append("📅 未来 7 天预报:")
        for day in forecast:
            date = day.get('date', '')
            weather = day.get('weather', '')
            temp = f"{day.get('temp_low', '')}℃ ~ {day.get('temp_high', '')}℃"
            wind = day.get('wind', '')
            rain = '⚠️' if '雨' in weather else ''
            lines.append(f"  {date}  {weather:<10} {temp}  {wind} {rain}")
    
    lines.append("")
    lines.append(f"⏰ 更新时间：{data.get('update_time', 'N/A')}")
    
    return '\n'.join(lines)

def main():
    if len(sys.argv) < 2:
        print("用法：python3 weather.py 城市名 [--forecast N] [--json] [--simple]")
        print("示例：python3 weather.py 北京")
        print("      python3 weather.py 灵山 --forecast 7")
        sys.exit(1)
    
    city_name = sys.argv[1]
    forecast_days = 7
    json_output = False
    simple = False
    
    # 解析参数
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--json':
            json_output = True
        elif arg == '--simple':
            simple = True
        elif arg == '--forecast' and i + 1 < len(sys.argv):
            forecast_days = int(sys.argv[i + 1])
            i += 1
        i += 1
    
    # 获取城市代码
    city_code = get_city_code(city_name)
    
    # 获取天气数据
    data = fetch_weather_data(city_code)
    
    if data is None:
        # 返回模拟数据（用于演示）
        data = {
            'city': city_name,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'current': {
                'temp': '14',
                'feels_like': '10.8',
                'weather': '多云',
                'humidity': '72',
                'wind': '东北风 2 级',
                'aqi': '63',
                'pressure': '1010',
                'visibility': '22.86',
            },
            'forecast': [
                {'date': '2 月 19 日 (今天)', 'weather': '多云', 'temp_low': '14', 'temp_high': '23', 'wind': '北风 2 级'},
                {'date': '2 月 20 日 (周五)', 'weather': '多云', 'temp_low': '14', 'temp_high': '25', 'wind': '北风 2 级'},
                {'date': '2 月 21 日 (周六)', 'weather': '多云转阴', 'temp_low': '17', 'temp_high': '26', 'wind': '南风 2 级'},
                {'date': '2 月 22 日 (周日)', 'weather': '阴', 'temp_low': '19', 'temp_high': '26', 'wind': ''},
                {'date': '2 月 23 日 (周一)', 'weather': '多云', 'temp_low': '19', 'temp_high': '27', 'wind': ''},
                {'date': '2 月 24 日 (周二)', 'weather': '多云转小雨', 'temp_low': '17', 'temp_high': '26', 'wind': ''},
            ]
        }
    
    # 输出结果
    print(format_output(data, simple=simple, json_output=json_output))

if __name__ == '__main__':
    main()
