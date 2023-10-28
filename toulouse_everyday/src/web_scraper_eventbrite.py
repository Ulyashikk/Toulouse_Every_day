import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import logging
import sqlite3

# Настройка логирования
logging.basicConfig(filename='my_log_eventbrite.log', level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def extract_event_info(soup):
    names = soup.find_all(class_ = 'Typography_root__4bejd #3a3247 Typography_body-lg__4bejd event-card__clamp-line--two Typography_align-match-parent__4bejd')
    dates = soup.find_all(class_ = 'Typography_root__4bejd #585163 Typography_body-md__4bejd event-card__clamp-line--one Typography_align-match-parent__4bejd')
    links = soup.find_all(class_ = 'event-card-link')
    images = soup.find_all(class_ = 'event-card-image')
    
    return names, dates,links, images

def get_items(locations_and_dates):
    locations = []
    dates=[]
    liens=[]
    images = []
    event_names = []

    for item in locations_and_dates:
        if "Tomorrow" not in item:
            if "Today" not in item:
                location, date, link, img, name = item.split(' = ')
                locations.append(location)
                dates.append(date)
                liens.append(link)
                images.append(img)
                event_names.append(name)
        
        return event_names, locations, dates, liens, images

def parse_and_update_data_eventbrite():
    try:
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        url = 'https://www.eventbrite.com/d/france--toulouse/all-events/'
        r = requests.get(url)

        if r.status_code==200:
            soup = bs(r.content, 'html.parser')

            names, dates, links, event_images = extract_event_info(soup)

            event_links = list(set(link.attrs['href'] for link in links))[1:]
            ev_images = list(set(image.attrs['src'] for image in event_images))[1:]

            event_dates = []
            for date in dates:
                date = date.text
                if date not in event_dates:
                    event_dates.append(date)

            event_date = event_dates[2:]

            locations_and_dates = []
            current_location = event_date[0]

            for item,link,img, name in zip(event_date,event_links,ev_images, names[::2]):
                if '•' in item:
                    current_location += " = " + item + " = " + link + " = " + img + " = " + name.text
                    locations_and_dates.append(current_location)
                current_location = item

            for el in locations_and_dates:
                els = el.split('•')
                if len(els)>2:
                    locations_and_dates.remove(el)

            event_names, locations, dates, event_links, images = get_items(locations_and_dates)

            date_deb = []
            date_fin = []

            month_dict = {
                            'Jan': '01', 'Fev': '02', 'Mar': '03', 'Avr': '04', 'May': '05', 'Jun': '06',
                            'Jul': '07', 'Aou': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                        }
            
            week_days = ['Monday ', 'Tuesday ', 'Wednesday ', 'Thursday ', 'Friday ', 'Saturday ', 'Sunday ']

            for date in dates:
                day, time = date.split('•')
                if '+' in time:
                    hour, h = time.split('+')
                    date_fin.append(hour)
                else: 
                    date_fin.append(time)
                if ',' in day:
                    times = day.split(',')
                    mois, jour = times[1].split()
                    mois = month_dict[mois]
                    date_deb.append(f'{jour}-{mois}')
                if day in week_days:
                    date_deb.append(day)

            
            for event_name, location, event_date_deb, event_date_fin, event_link, event_img in zip(event_names, locations, date_deb, date_fin, event_links, images):
                response = requests.get(event_img)
                image_data = response.content 

                cursor.execute("INSERT INTO events (name, description, date_deb, date_fin, type, link, image) VALUES (?, ?, ?, ?, ?, ?, ?)", (event_name, location, event_date_deb, event_date_fin, '', event_link, image_data))

            conn.commit()
            conn.close()

        else:
            print('Error page code: %s' % r.status_code)
    
    except Exception as e:
        logging.error("Error web-parsing code : %s" % str(e), exc_info=True)

if __name__ == "__main__":
    logging.info("Starting web-parsing...")
    parse_and_update_data_eventbrite()
    logging.info("Web-parsing completed successfully.")