import time
from datetime import datetime, timedelta

from data_model import Scraper, Website
from listings import ListingsScraper


def run_daily_scraping(scraper: Scraper) -> None:
    while True:
        # Get the current date and time
        current_time = datetime.now()

        # Set the time to run the script every day at a specific hour and minute
        scheduled_time = current_time.replace(
            hour=12, minute=0, second=0, microsecond=0
        )

        # Check if the current time is equal to or past the scheduled time
        if current_time >= scheduled_time:
            # Run the scraping function with the scraper as an argument
            scraper.scrape_job_listings()

            # Update the scheduled time for the next day
            scheduled_time += timedelta(days=1)

        # Calculate the time until the next scheduled run
        time_until_next_run = scheduled_time - current_time

        # Sleep until the next scheduled run
        time.sleep(time_until_next_run.total_seconds())


if __name__ == "__main__":
    try:
        listings_website = Website("https://www.artjobs.com/open-calls")
        listings_scraper = ListingsScraper(listings_website, "listings")
        run_daily_scraping(listings_scraper)
    except Exception as e:
        print(f"An error occurred: {e}")
