from typing import List
from data_model import Website, Scraper

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials


from typing import List
from data_model import Website, Scraper

class ArtJobsScraper(Scraper):
    def __init__(self, website: Website):
        super().__init__(website)

    def scrape(self) -> None:
        base_url = self.website.url
        add_fields = [
            'open-call-type',
            'category-addapost',
            'call-type',
            'open-call-theme',
            'tags-news-country',
            'tags-news-city',
            'organisation',
            'eligibility',
            'tags-news'
        ]
        total_pages = self.get_total_pages(base_url)

        while True:
            current_time = datetime.now()
            scheduled_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)

            if current_time >= scheduled_time:
                self.scrape_job_listings(base_url, add_fields, total_pages)
                scheduled_time += timedelta(days=1)

            time_until_next_run = scheduled_time - current_time
            time.sleep(time_until_next_run.total_seconds())

    def scrape_job_listings(self, base_url: str, add_fields: List[str], total_pages: int) -> None:
        row_counter = 0
        sheet = self.authenticate_google_sheets("Listings")

        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}?page={page_num}"

            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_listings = soup.find_all('tr')

                for job in job_listings:
                    section = job.find('td', class_="views-field views-field-title")

                    try:
                        link = section.find('a')['href']
                        link = f"https://www.artjobs.com{link}"
                    except (AttributeError, TypeError):
                        link = ""

                    try:
                        title = section.find('a').text
                    except (AttributeError, TypeError):
                        title = ""

                    try:
                        deadline = section.find('span', class_='date-display-single').text
                    except (AttributeError, TypeError):
                        deadline = ""

                    additional_info = self.fetch_additional_info(link, add_fields)

                    new_row = [link, title, deadline] + additional_info
                    try: 
                        deadline_passed = datetime.strptime(deadline, "%m/%d/%Y") <= datetime.now()
                        if deadline_passed:
                            pass
                        else: sheet.append_row(new_row)
                    except ValueError:
                        sheet.append_row(new_row)

                    row_counter += 1

                    if row_counter >= MAX_ROWS_BEFORE_SLEEP:
                        print(f"Sleeping for {SLEEP_DURATION} seconds to avoid rate limit...")
                        time.sleep(SLEEP_DURATION)
                        row_counter = 0

                    print(f"Link: {link}\n Title: {title}\n Deadline: {deadline}\n{'='*30}")
            else:
                print(f"Failed to fetch data for page {page_num}. Status code: {response.status_code}")

    def fetch_additional_info(self, link: str, add_fields: List[str]) -> List[str]:
        response = requests.get(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            additional_info = []

            for t in add_fields:
                base_class = self.get_class(soup, t, "taxonomy-term-reference", "field-label-inline clearfix")

                try:
                    add_field = soup.find('div', class_=base_class)
                    keywords = add_field.find('ul').find_all('li')
                    keys = [k.find('a').text for k in keywords]
                except (AttributeError, TypeError):
                    keys = []

                additional_info.append(" ".join(keys))

            try:
                desc_class = self.get_class(soup, "description", "text-long", "field-label-hidden")
                desc_range = soup.find('div', class_=desc_class)
                desc_fields = desc_range.find_all('p')
                description = [d.text for d in desc_fields]
            except (AttributeError, TypeError):
                description = []

            additional_info.append(" ".join(description))

            return additional_info
        else:
            print(f"Failed to fetch additional information for link {link}. Status code: {response.status_code}")
            return [""]

    def get_class(self, soup, element: str, reference: str, field_label: str) -> str:
        return f"field field-name-field-{element} field-type-{reference} {field_label}"

    def get_total_pages(self, url: str) -> int:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            pager_items = soup.find_all('li', class_='pager-item')
            return max([int(item.text.strip()) for item in pager_items], default=1)
        else:
            return 1

    def authenticate_google_sheets(self, sheet_name: str):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)
        client = gspread.authorize(credentials)
        spreadsheet = client.open(sheet_name)
        sheet = spreadsheet.sheet1
        return sheet
