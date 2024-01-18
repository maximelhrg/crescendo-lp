from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


class Website:
    def __init__(self, url: str):
        self.url = url


class Scraper:
    def __init__(self, website: Website, collection_name: str):
        self.website = website
        self.collection_name = collection_name
        self.firestore_client = firestore.Client()

    def entry_exists(self, job_data: dict) -> bool:
        # Check if the entry already exists in Firestore
        collection_ref = self.firestore_client.collection(self.collection_name)
        query = collection_ref
        query = (
            query.where(filter=FieldFilter("link", "==", job_data["link"]))
            .limit(1)
            .stream()
        )

        return any(query)

    def remove_expired_entries(self) -> None:
        # Remove expired entries from Firestore
        collection_ref = self.firestore_client.collection(self.collection_name)
        current_date = datetime.now()

        # Query for entries with deadlines before or equal to today
        query = collection_ref.where(
            filter=FieldFilter("deadline", "<=", current_date.strftime("%m/%d/%Y"))
        ).stream()

        for entry in query:
            entry.reference.delete()

    def save_to_firestore(self, job_data: dict) -> None:
        # Save data to Firestore
        collection_ref = self.firestore_client.collection(self.collection_name)
        collection_ref.add(job_data)

    def scrape_elements(
        self, url: str, element_type: str, class_name: str
    ) -> List[BeautifulSoup]:
        # Scrape elements of a specific type with a given class from a webpage
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            if class_name:
                elements = soup.find_all(element_type, class_=class_name)
            else:
                elements = soup.find_all(element_type)
            return elements
        else:
            print(
                f"Failed to fetch data from {url}. Status code: {response.status_code}"
            )
            return []

    def fetch_info(self, job: str, element_type: str, class_name: str) -> BeautifulSoup:
        # Fetch section from a specific job
        try:
            if class_name:
                section = job.find(element_type, class_=class_name)
            else:
                section = job.find(element_type)
            return section
        except (AttributeError, TypeError):
            return ""

    def get_total_pages(self, element_type: str, class_name: str) -> int:
        # Get the total number of pages from the website
        url = self.website.url
        pager_items = self.scrape_elements(url, element_type, class_name)

        return max([int(item.text.strip()) for item in pager_items], default=1)
