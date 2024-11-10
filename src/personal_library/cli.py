import json
import csv
from typing import List, Dict
from .book_metadata import BookMetadataFetcher

def process_books(books_list: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """
    Process a list of books and return found and unfound books.
    """
    fetcher = BookMetadataFetcher()
    found_books = []
    unfound_books = []

    for book in books_list:
        results = fetcher.search_book(book["title"], book["author"])
        if results:
            # Take the first result as the best match
            found_books.append(fetcher.format_book_data(results[0]))
        else:
            unfound_books.append(book)

    return found_books, unfound_books

def export_to_csv(books: List[Dict], output_file: str = "library_thing_import.csv"):
    """
    Export books to CSV in LibraryThing format.
    """
    headers = ['TITLE', 'AUTHOR (last, first)', 'DATE', 'ISBN', 'PUBLICATION INFO',
              'TAGS', 'RATING', 'REVIEW', 'DATE READ', 'PAGE COUNT', 'CALL NUMBER']

    rows = [headers]
    for book in books:
        # Handle author name formatting
        author_parts = book['author'].split(', ')
        if len(author_parts) == 1:
            author_parts = book['author'].split(' ')
        author = f"{author_parts[-1]}, {' '.join(author_parts[:-1])}"

        # Create publication info
        pub_info = f"{book['publisher']} ({book['publish_date']}), {book['number_of_pages']} pages"

        rows.append([
            book['title'],
            author,
            book['publish_date'],
            book['isbn'],
            pub_info,
            '',  # TAGS
            '0',  # RATING
            '',  # REVIEW
            '',  # DATE READ
            book['number_of_pages'],
            ''  # CALL NUMBER
        ])

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def main():
    # Sample books list - you might want to load this from a file in practice
    books = [
        {"title": "Principles", "author": "Ray Dalio"},
        {"title": "In the Realm of Hungry Ghosts", "author": "Gabor Mate"},
        {"title": "The Organized Mind", "author": "Daniel J. Levitin"},
    ]

    print("Processing books...")
    found_books, unfound_books = process_books(books)

    # Export results
    if found_books:
        export_to_csv(found_books)
        print(f"\nExported {len(found_books)} books to library_thing_import.csv")

    if unfound_books:
        print("\nUnfound books:")
        for book in unfound_books:
            print(f"- {book['title']} by {book['author']}")

if __name__ == "__main__":
    main()
