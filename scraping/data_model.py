from typing import List
from pydantic import BaseModel

class Website(BaseModel):
    url: str

    def get_html(self) -> str:
        # Implement logic to get HTML content from the website
        pass

    def extract_data(self, html: str) -> List[str]:
        # Implement logic to extract data from the HTML
        pass


class Scraper:
    def __init__(self, website: Website):
        self.website = website

    def scrape(self) -> None:
        # Implement the scraping logic here
        # You can use self.website to access website-specific methods and properties
        pass