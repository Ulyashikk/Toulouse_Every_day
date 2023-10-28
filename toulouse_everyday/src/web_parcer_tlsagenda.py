from web_scraper_tlsagenda import parse_and_update_data
from web_scraper_eventbrite import parse_and_update_data_eventbrite
import schedule
import time

schedule.every().day.at("14:35").do(parse_and_update_data)
schedule.every().day.at("14:35").do(parse_and_update_data_eventbrite)

while True:
    schedule.run_pending()
    time.sleep(1)