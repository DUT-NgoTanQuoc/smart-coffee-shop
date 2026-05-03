from django.test import Client
c=Client()
r=c.post('/accounts/login/', {'username':'admin','password':'admin123'}, follow=True)
print('login status', r.status_code)
r2=c.get('/staff/schedule/')
print('schedule status', r2.status_code)
print('has calendar div:', '<div id="staffCalendar">' in r2.content.decode('utf-8'))
open('scripts/schedule_page_auth2.html','wb').write(r2.content)
print('saved to scripts/schedule_page_auth2.html')
