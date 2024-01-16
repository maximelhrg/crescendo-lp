import time
from datetime import datetime, timedelta

import gspread
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

# Define the maximum rows to append before sleeping
MAX_ROWS_BEFORE_SLEEP = 60
# Define the sleep duration in seconds
SLEEP_DURATION = 60  # Adjust as needed


def authenticate_google_sheets(sheet_name):
    # Set up Google Sheets API credentials
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "./credentials.json", scope
    )
    client = gspread.authorize(credentials)

    # Open the Google Spreadsheet by title
    spreadsheet = client.open(sheet_name)

    # Select the first sheet in the spreadsheet
    sheet = spreadsheet.sheet1

    return sheet


def scrape_job_listings(sheet, base_url, add_fields, total_pages):
    row_counter = 0

    for page_num in range(1, total_pages + 1):
        # Adjust the URL for the first page
        if page_num == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page_num}"

        # Send a GET request to the website
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract and print job listings or perform other desired actions
            job_listings = soup.find_all("tr")

            for job in job_listings:
                section = job.find("td", class_="views-field views-field-title")

                try:
                    link = section.find("a")["href"]
                    link = f"https://www.artjobs.com{link}"
                except (AttributeError, TypeError):
                    link = ""

                try:
                    title = section.find("a").text
                except (AttributeError, TypeError):
                    title = ""

                try:
                    deadline = section.find("span", class_="date-display-single").text
                except (AttributeError, TypeError):
                    deadline = ""

                # Fetch additional information from the linked page
                additional_info = fetch_additional_info(link, add_fields)

                # Insert the job data as a new row if deadline has not been met (or is not specified)
                new_row = [link, title, deadline] + additional_info
                try:
                    deadline_passed = (
                        datetime.strptime(deadline, "%m/%d/%Y") <= datetime.now()
                    )
                    if deadline_passed:
                        pass
                    else:
                        sheet.append_row(new_row)  # , index=2)
                except ValueError:
                    sheet.append_row(new_row)  # , index=2)

                row_counter += 1

                if row_counter >= MAX_ROWS_BEFORE_SLEEP:
                    print(
                        f"Sleeping for {SLEEP_DURATION} seconds to avoid rate limit..."
                    )
                    time.sleep(SLEEP_DURATION)
                    row_counter = 0

                print(f"Link: {link}\n Title: {title}\n Deadline: {deadline}\n{'='*30}")
        else:
            print(
                f"Failed to fetch data for page {page_num}. Status code: {response.status_code}"
            )


def fetch_additional_info(link, add_fields):
    # Fetch additional information from the linked page
    response = requests.get(link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        def get_class(element, reference, field_label):
            return (
                f"field field-name-field-{element} field-type-{reference} {field_label}"
            )

        additional_info = []
        for t in add_fields:
            base_class = get_class(
                t, "taxonomy-term-reference", "field-label-inline clearfix"
            )

            try:
                add_field = soup.find("div", class_=base_class)

                keywords = add_field.find("ul").find_all("li")
                keys = []
                for k in keywords:
                    keys.append(k.find("a").text)

            except (AttributeError, TypeError):
                keys = []

            additional_info.append(" ".join(keys))

        try:
            desc_class = get_class("description", "text-long", "field-label-hidden")
            desc_range = soup.find("div", class_=desc_class)
            desc_fields = desc_range.find_all("p")
            description = [d.text for d in desc_fields]
            # description = description[0:1]  # Limit description to first items?

        except (AttributeError, TypeError):
            description = []

        additional_info.append(" ".join(description))

        return additional_info
    else:
        print(
            f"Failed to fetch additional information for link {link}. Status code: {response.status_code}"
        )
        return [""]


def get_total_pages(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        pager_items = soup.find_all("li", class_="pager-item")
        return max([int(item.text.strip()) for item in pager_items], default=1)
    else:
        return 1


def run_daily_scraping(sheet, base_url, add_fields):
    total_pages = get_total_pages(base_url)

    while True:
        # Get the current date and time
        current_time = datetime.now()

        # Set the time to run the script every day at a specific hour and minute
        scheduled_time = current_time.replace(
            hour=12, minute=0, second=0, microsecond=0
        )

        # Check if the current time is equal to or past the scheduled time
        if current_time >= scheduled_time:
            # Run the scraping function with the Google Sheet, base URL, and total pages as arguments
            scrape_job_listings(sheet, base_url, add_fields, total_pages)

            # Update the scheduled time for the next day
            scheduled_time += timedelta(days=1)

        # Calculate the time until the next scheduled run
        time_until_next_run = scheduled_time - current_time

        # Sleep until the next scheduled run
        time.sleep(time_until_next_run.total_seconds())


if __name__ == "__main__":
    # Additional fields
    add_fields = [
        "open-call-type",
        "category-addapost",
        "call-type",
        "open-call-theme",
        "tags-news-country",
        "tags-news-city",
        "organisation",
        "eligibility",
        "tags-news",
    ]

    google_sheet = authenticate_google_sheets("Listings")
    base_url = "https://www.artjobs.com/open-calls/us"
    run_daily_scraping(google_sheet, base_url, add_fields)
