import random
import time

import requests
from bs4 import BeautifulSoup
from data_model import Scraper, Website


class AdditionalInfoFetcher:
    def __init__(self, link, add_fields):
        self.link = link
        self.add_fields = add_fields

    def fetch_additional_info(self):
        # Fetch additional information from the linked page
        response = requests.get(self.link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            additional_info = []

            for t in self.add_fields:
                base_class = self._get_class(
                    t, "taxonomy-term-reference", "field-label-inline clearfix"
                )

                try:
                    add_field = soup.find("div", class_=base_class)
                    keywords = add_field.find("ul").find_all("li")
                    keys = [k.find("a").text for k in keywords]

                except (AttributeError, TypeError):
                    keys = []

                additional_info.append(" ".join(keys))

            try:
                desc_class = self._get_class(
                    "description", "text-long", "field-label-hidden"
                )
                desc_range = soup.find("div", class_=desc_class)
                desc_fields = desc_range.find_all("p")
                description = [d.text for d in desc_fields]

            except (AttributeError, TypeError):
                description = []

            additional_info.append(" ".join(description))
            return additional_info
        else:
            print(
                f"Failed to fetch additional information for link {self.link}. Status code: {response.status_code}"
            )
            return [""]

    def _get_class(self, element, reference, field_label):
        return f"field field-name-field-{element} field-type-{reference} {field_label}"


class ListingsScraper(Scraper):
    def __init__(self, website: Website, collection_name: str):
        super().__init__(website, collection_name)

    def scrape_job_listings(self) -> None:
        total_pages = self.get_total_pages("li", "pager-item")
        ref_element_type = "td"
        ref_class_name = "views-field views-field-title opencalltitle"
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

        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                url = self.website.url
            else:
                url = f"{self.website.url}?page={page_num}"

            job_listings = self.scrape_elements(url, "tr", None)

            for job in job_listings:
                try:
                    section = self.fetch_info(job, ref_element_type, ref_class_name)
                    link = self.fetch_info(section, "a", None)["href"]
                    link = f"https://www.artjobs.com{link}"

                    title = self.fetch_info(section, "a", None).text

                    deadline = self.fetch_info(
                        section, "span", "date-display-single"
                    ).text

                    additional_info_fetcher = AdditionalInfoFetcher(link, add_fields)
                    additional_info = additional_info_fetcher.fetch_additional_info()
                    keywords, description = additional_info[:-1], additional_info[-1]

                    job_data = {
                        "link": link,
                        "title": title,
                        "deadline": deadline,
                        "description": description,
                        "keywords": keywords,
                    }
                    # Check if entry already exists in Firestore
                    if not self.entry_exists(job_data):
                        # Save data to Firestore
                        self.save_to_firestore(job_data)

                    print(
                        f"Link: {link}\nTitle: {title}\nDeadline: {deadline}\n{'='*30}"
                    )

                except (AttributeError, TypeError):
                    pass

            # Introduce a random delay between pages
            delay_seconds = random.uniform(1, 3)
            time.sleep(delay_seconds)
            print(f"Waiting {delay_seconds} seconds before fetching new page")

        # Remove expired entries from Firestore
        self.remove_expired_entries()


if __name__ == "__main__":
    listings_website = Website("https://www.artjobs.com/open-calls")
    collection_name = "listings"
    listings_scraper = ListingsScraper(listings_website, collection_name)
    listings_scraper.scrape_job_listings()
