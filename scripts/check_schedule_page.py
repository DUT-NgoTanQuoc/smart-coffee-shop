import requests
r = requests.get('http://127.0.0.1:8000/staff/schedule/')
print('Status:', r.status_code)
print('Has calendar container:', '<div id="staffCalendar">' in r.text)
open('scripts/schedule_page.html','w',encoding='utf-8').write(r.text)
print('Saved to scripts/schedule_page.html')
