import telebot
import config
import sqlite3
import schedule
import time

from PIL import Image
from io import BytesIO

bot = telebot.TeleBot(config.TOKEN)

#to send a message to the telegram channel
def send_message(event):
    name, description, date_deb, date_fin, type, link, image_data = event

    month_dict = {
        '01': 'jan', '02': 'fév', '03': 'mar', '04': 'avr', '05': 'mai', '06': 'jun',
        '07': 'jul', '08': 'aoû', '09': 'sep', '10': 'oct', '11': 'nov', '12': 'déc'
    }

    if len(date_deb) <= 7:
        day, month = date_deb.split('-')
        month = month_dict.get(month, month)
        date_deb = f"{day} {month}"

    message_text = f"❗️{name}❗️\n\n 🗓{date_deb}"
    
    if date_fin:
        message_text += f" -{date_fin}"
    
    message_text += f"\n\n--<i>{type}</i>--\n{description}\n<a href='{link}'>Pour plus d'informations..</a>"

    image = Image.open(BytesIO(image_data))
    
    bot.send_photo(chat_id=config.channel_username, photo=image, caption=message_text, parse_mode="HTML")

#to send messages and to delete duplicates
def send_messages():
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    
    # sort events by date
    cursor.execute("SELECT name, description, date_deb, date_fin, type, link, image FROM events ORDER BY date_deb")
    events = cursor.fetchall()

    #limiting the number of send messages
    for event in events[:2]:
        send_message(event)
        name, *_ = event
        cursor.execute("DELETE FROM events WHERE name =?", (name,))
    
    conn.commit()
    conn.close()

# send_messages()


schedule.every().day.at("09:30").do(send_messages)
schedule.every().day.at("11:30").do(send_messages)
schedule.every().day.at("15:00").do(send_messages)
schedule.every().day.at("18:00").do(send_messages)

while True:
    schedule.run_pending()
    time.sleep(1)
