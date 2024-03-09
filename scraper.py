import re
import json
import datetime
from zoneinfo import ZoneInfo
import html

import requests

from db import get_db_conn

URL = 'https://visitseattle.org/events/page/'
URL_LIST_FILE = './data/links.json'
URL_DETAIL_FILE = './data/data.json'


def list_links():
    # Function to scrape event links from the website and store them in a JSON file
    res = requests.get(URL + '1/')
    last_page_no = int(re.findall(r'bpn-last-page-link"><a href=".+?/page/(\d+?)/.+" title="Navigate to last page">', res.text)[0])

    links = []
    for page_no in range(1, last_page_no + 1):
        res = requests.get(URL + str(page_no) + '/')
        links.extend(re.findall(r'<h3 class="event-title"><a href="(https://visitseattle.org/events/.+?/)" title=".+?">.+?</a></h3>', res.text))

    json.dump(links, open(URL_LIST_FILE, 'w'))

def get_event_details(link):
    # Function to scrape detailed information about a single event from the event link
    try:
        row = {}
        res = requests.get(link)
        row['title'] = html.unescape(re.findall(r'<h1 class="page-title" itemprop="headline">(.+?)</h1>', res.text)[0])
        datetime_venue = re.findall(r'<h4><span>.*?(\d{1,2}/\d{1,2}/\d{4})</span> \| <span>(.+?)</span></h4>', res.text)[0]
        row['date'] = datetime.datetime.strptime(datetime_venue[0], '%m/%d/%Y').replace(tzinfo=ZoneInfo('America/Los_Angeles')).isoformat()
        row['venue'] = datetime_venue[1].strip()
        metas = re.findall(r'<a href=".+?" class="button big medium black category">(.+?)</a>', res.text)
        row['category'] = html.unescape(metas[0])
        row['location'] = metas[1]
        return row
    except IndexError as e:
        print(f'Error: {e}')
        print(f'Link: {link}')
        return None


def scrape_events_data(links):
    # Function to scrape detailed information about events from a list of event links
    data = []
    for link in links:
        event_data = get_event_details(link)
        if event_data:
            data.append(event_data)
    return data


def insert_events_to_db(events):
    # Function to insert scraped event data into a PostgreSQL database
    q = '''
    CREATE TABLE IF NOT EXISTS events (
        url TEXT PRIMARY KEY,
        title TEXT,
        date TIMESTAMP WITH TIME ZONE,
        venue TEXT,
        category TEXT,
        location TEXT
    );
    '''
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(q)

    for event in events:
        q = '''
        INSERT INTO events (url, title, date, venue, category, location)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        '''
        cur.execute(q, (event['url'], event['title'], event['date'], event['venue'], event['category'], event['location']))


if __name__ == '__main__':
    list_links()
    links = json.load(open(URL_LIST_FILE, 'r'))
    events_data = scrape_events_data(links)
    insert_events_to_db(events_data)
