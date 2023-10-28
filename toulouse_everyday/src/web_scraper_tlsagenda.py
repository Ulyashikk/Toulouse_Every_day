# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from time import sleep
import logging
import sqlite3
import re

# logging configuration settings
logging.basicConfig(filename='my_log.log', level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def create_database_table(cursor):
    # creation table for events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            date_deb DATE, 
            date_fin TEXT,
            type TEXT,
            link TEXT,
            image BLOB
        )
    ''')

# transfroming data to images in url format
def event_to_img(event_pics):
    event_pic = [] 
    for pic in event_pics:
        img = pic.find('img')
        event_pic.append(img['src'])
    return event_pic
            
#data from hrml file to list of strings
def create_list(arr):
    list = []
    for item in arr:
        list.append(item.text)
    return list
            
#data from hrml file to list of strings without spaces and other special characters
def list_clean(arr):
    list = []
    for date in arr:
        list.append(date.text.strip())
    return list

#date from hrml file to list of links by adding the base url
def get_link(link_elements):
    event_links = []
    base_url = 'https://www.toulouse-tourisme.com/'
    for link_element in link_elements:
        if link_element:
            relative_link = link_element.find('a')['href']
            absolute_link = urljoin(base_url, relative_link)
            event_links.append(absolute_link)
    return event_links


#exptracting data from hrml file to list of elements
def extract_event_info(soup):
    event_names = create_list(soup.find_all('h2'))
    event_resume = create_list(soup.find_all(class_='resume'))
    event_type = list_clean(soup.find_all(class_='type'))
    event_pics = event_to_img(soup.find_all('div', class_='ds-1col entity entity-field-collection-item field-collection-item-col-photos view-mode-accroche'))
    event_date = create_list(soup.find_all('div', class_='dates'))
    event_links = get_link(soup.find_all('div', class_='lien'))

    event_links = event_links[18:]
    event_names = event_names[20:44]
    
    return event_names, event_resume, event_type, event_pics, event_date, event_links


def process_dates(event_date):
            # regular expression to find dates in hrml file
            date_pattern = re.compile(r'(\d{1,2} [a-zA-Zûé]{3})[àau]+(\d{1,2} [a-zA-Z]{3})')

            formatted_dates = []

            for date_string in event_date:

                matches = date_pattern.findall(date_string)

                if matches:
                    # "21 octau22 oct"
                    for match in matches:
                        start_date, end_date = match
                        formatted_dates.append(f'{start_date} - {end_date}')
                else:
                    # a single date
                    date_match = re.search(r'(\d{1,2} [a-zA-Zûé]{3}[^\d]+)+', date_string)
                    if date_match:
                        # multiple dates
                        dates = date_string.split('\n')
                        dates = [date.strip() for date in dates if date.strip()]
                        dates = [date for date in dates if len(date) <= 6]
                        dates = dates[:5]

                        formatted_dates.append(', '.join(dates))
                    else:
                        formatted_dates.append(date_match.group(0))

            #dictionary to map month abbreviations to numbers
            month_dict = {
                'jan': '01', 'fév': '02', 'mar': '03', 'avr': '04', 'mai': '05', 'jun': '06',
                'jul': '07', 'aoû': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'déc': '12'
            }

            date_deb = []
            date_fin = []
            for date in formatted_dates:
                if len(date)<=6:
                    day, month_abbrev = date.split()
                    month = month_dict.get(month_abbrev.lower(), '00')
                    formatted_date = f'{day}-{month}'

                    date_deb.append(formatted_date)
                    date_fin.append('')
                if '-' in date:
                    dates = date.split('-')
                    day, month_abbrev = dates[0].split()
                    month = month_dict.get(month_abbrev.lower(), '00')

                    date_deb.append(f'{day}-{month}')
                    date_fin.append(dates[1])
                if ',' in date:
                    dates = date.split(',')
                    day, month_abbrev = dates[0].split()
                    month = month_dict.get(month_abbrev.lower(), '00')

                    date_deb.append(f'{day}-{month}')
                    date_fin.append(', '.join(dates[1::]))
                    
            return date_deb, date_fin


def check_and_remove_duplicate(cursor, name):
    cursor.execute("SELECT id FROM events WHERE name=?", (name,))
    row = cursor.fetchone()
    
    if row:
        # delete duplicates if exists
        event_id = row[0]
        cursor.execute("DELETE FROM events WHERE id=?", (event_id,))


def insert_data(cursor, event_name, event_description, event_date_deb, event_date_fin, event__type, event_link, event_img):
                response = requests.get(event_img)
                image_data = response.content 
                # add data to database
                cursor.execute("INSERT INTO events (name, description, date_deb, date_fin, type, link, image) VALUES (?, ?, ?, ?, ?, ?, ?)", (event_name, event_description, event_date_deb, event_date_fin, event__type, event_link, image_data))


def parse_and_update_data():
    try:
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        create_database_table(cursor)

        for count in range(5):
            sleep(1)

            url = f'https://www.toulouse-tourisme.com/agenda?page={count}'

            r = requests.get(url)

            if r.status_code == 200:

                soup = bs(r.content, 'html.parser')

                event_names, event_resume, event_type, event_pics, event_date, event_links = extract_event_info(soup)

                logging.info(event_date)

                date_deb, date_fin = process_dates(event_date)

                # logging.info(event_names)
                # logging.info(event_resume)
                # logging.info(date_deb)
                # logging.info(date_fin)
            
                for event_name, event_description, event_date_deb, event_date_fin, event__type, event_link, event_img in zip(event_names, event_resume, date_deb, date_fin, event_type, event_links, event_pics):
                    check_and_remove_duplicate(cursor, event_name)
                    insert_data(cursor, event_name, event_description, event_date_deb, event_date_fin, event__type, event_link, event_img)

            else:
                print('Error page code: %s' % r.status_code)

        conn.commit()
        conn.close()
    
    except Exception as e:
        logging.error("Error web-parsing code : %s" % str(e), exc_info=True)

if __name__ == "__main__":
    logging.info("Starting web-parsing...")
    parse_and_update_data()
    logging.info("Web-parsing completed.")