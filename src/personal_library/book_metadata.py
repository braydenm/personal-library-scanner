import requests
from typing import List, Dict, Optional

class BookMetadataFetcher:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1/volumes"

    def search_book(self, title: str, author: Optional[str] = None) -> List[Dict]:
        """Search for books using Google Books API."""
        query = f"intitle:{title}"
        if author:
            query += f"+inauthor:{author}"

        params = {
            "q": query,
            "maxResults": 3
        }

        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])[:3]
        return []

    @staticmethod
    def get_isbn(identifiers: List[Dict]) -> str:
        """Extract ISBN from book identifiers."""
        for identifier in identifiers:
            if identifier['type'] in ['ISBN_13', 'ISBN_10']:
                return identifier['identifier']
        return 'N/A'

    def format_book_data(self, book_item: Dict) -> Dict:
        """Format book data into a consistent structure."""
        volume_info = book_item.get("volumeInfo", {})
        return {
            "title": volume_info.get("title", ""),
            "author": ", ".join(volume_info.get("authors", [])),
            "publish_date": volume_info.get("publishedDate", ""),
            "isbn": self.get_isbn(volume_info.get('industryIdentifiers', [])),
            "publisher": volume_info.get("publisher", ""),
            "number_of_pages": volume_info.get("pageCount", ""),
        }
