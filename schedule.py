from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from ics import Calendar, Event
from datetime import *
from dateutil import *

start_times = []
end_times = []
subjects = []
teachers = []

url = 'http://planzajec.uek.krakow.pl/index.php?typ=G&id=171611&okres=2'
request = requests.get(url)
html = urlopen(request.url)
bs = BeautifulSoup(html, 'html.parser')

#print(bs.prettify())

utc_zone = tz.tzutc()
local_zone = tz.tzlocal()

for index, row in enumerate(bs.find_all('tr')):
    if index == 0:
        #print(row)
        headers = row.find_all('th')
        columns = ['Start',
                   'Koniec',
                   headers[2].text.strip(),
                   headers[-2].text.strip()]
    else:
        date = row.find('td', {'class':'termin'})
        time = row.find('td', {'class':'dzien'})
        start_time = date.text.strip() + ' ' + time.text.strip()[3:8] + ':00'
        local_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        local_time = local_time.replace(tzinfo=local_zone)
        utc_time = local_time.astimezone(utc_zone)
        utc_string = utc_time.strftime('%Y-%m-%d %H:%M:%S')
        start_times.append(utc_string)
        end_time = date.text.strip() + ' ' + time.text.strip()[11:16] + ':00'
        local_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        local_time = local_time.replace(tzinfo=local_zone)
        utc_time = local_time.astimezone(utc_zone)
        utc_string = utc_time.strftime('%Y-%m-%d %H:%M:%S')
        end_times.append(utc_string)
        subject = row.find_all('td')[-4].text.strip()
        typed = row.find_all('td')[-3].text.strip().split(' ')[0]
        subject = subject + ' - ' + typed
        subjects.append(subject)
        teacher = row.find_all('td')[-2]
        teachers.append(teacher.text.strip())


zipped_list = list(zip(start_times, end_times, subjects, teachers))
df = pd.DataFrame(zipped_list, columns=columns)

#print(df)

replacement = 'Marketing strategiczny'
df['Przedmiot'] = df['Przedmiot'].replace(replacement, np.nan)
df = df.dropna().reset_index(level=0)

#df.to_csv('schedulee.csv')

c = Calendar()

for index, row in df.iterrows():
    e = Event()
    name = row['Przedmiot']
    begin = row['Start']
    end = row['Koniec']
    description = row['Nauczyciel']

    e.name = name
    e.begin = begin
    e.end = end
    e.description = description

    c.events.add(e)

    #print(e)

#print(c.events)

with open('studies.ics', 'w') as f:
    f.writelines(c)