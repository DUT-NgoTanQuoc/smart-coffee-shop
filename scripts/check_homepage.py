import requests

r = requests.get('http://127.0.0.1:8000/')
content = r.text
for s in ['Doanh thu hôm nay','Chờ xử lý','Dự đoán doanh thu','Tổng quan dự báo 30 ngày','Top 5 bán chạy']:
    print(s, '->', 'OK' if s in content else 'MISSING')
