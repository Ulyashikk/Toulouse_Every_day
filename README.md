# Toulouse_Every_day
Automated Event Scraping and Notification System

Objective:
To develop an automated system for scraping event information from multiple websites, publishing data in the 'Toulouse. Every Day' Telegram channel, and delivering event details to users through a Telegram bot. The web scraping, updates, and message delivery occur automatically every day.

Technologies Used:
Python
SQLite
BeautifulSoup
Telebot (Python Telegram Bot API)
Schedule (Python Job Scheduling)
Git/GitHub

Summary:
The "Automated Event Scraping and Notification System" project is designed to streamline the process of gathering event information from various websites, publishing this data in the 'Toulouse. Every Day' Telegram channel, and providing users with timely event updates through a Telegram bot. The system leverages web scraping, database management, and scheduled notifications to deliver a comprehensive solution.

Features:
Web Scraping: The project uses BeautifulSoup to extract event data from specific websites. It scrapes event names, descriptions, dates, types, links, locations and event images.

Database Management: Event data is stored in an SQLite database, allowing for efficient retrieval, manipulation, and scheduling of notifications.

Scheduled Notifications: The project employs the "schedule" library to automate the delivery of event notifications to users through a Telegram bot. Users receive event details, including names, descriptions, dates, and links, along with event images.

Automatic Publication: Event data is automatically published in the 'Toulouse. Every Day' Telegram channel to reach a wider audience.

Data Cleaning: The system ensures that event data is cleaned and optimized for presentation to users. This includes formatting dates, handling single and multiple date formats, and removing duplicate events.

Accomplishments:
Successfully implemented web scraping to gather event information from source websites.
Developed a Python script to schedule event notifications for users.
Integrated SQLite to store event data, ensuring efficient data management.
Achieved the automatic cleanup of date formats and the removal of duplicate events.
Created a Telegram bot to deliver event details and images to users.
Future Enhancements:
Implement natural language processing for better event categorization.
Expand web scraping capabilities to cover more event sources.
Utilisation of Google Cloud SQl.

Conclusion:
The "Automated Event Scraping and Notification System" project is an innovative solution that automates the process of event information delivery to users. Its efficient web scraping, database management, and scheduled notifications make it a versatile tool for event enthusiasts. The system is designed to update event data and send notifications automatically every day.
