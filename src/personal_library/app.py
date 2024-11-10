import streamlit as st
from personal_library.book_metadata import BookMetadataFetcher
from personal_library.camera import camera_input
from personal_library.book_detection import BookDetector
import json

def add_book(title: str, author: str):
    """Add a new book to books_to_process"""
    if not title:  # Skip empty titles
        return

    if 'books_to_process' not in st.session_state:
        st.session_state.books_to_process = []

    new_book = {"title": title, "author": author}
    st.session_state.books_to_process.append(new_book)

    # Clear the input fields by removing them from session state
    del st.session_state.new_title
    del st.session_state.new_author

def load_sample_books():
    """Load sample books into books_to_process"""
    sample_books = [
        {"title": "Principles", "author": "Ray Dalio"},
        {"title": "In the Realm of Hungry Ghosts", "author": "Gabor Mate"},
        {"title": "The Organized Mind", "author": "Daniel J. Levitin"}
    ]

    if 'books_to_process' not in st.session_state:
        st.session_state.books_to_process = []

    st.session_state.books_to_process.extend(sample_books)

def main():
    st.title("Personal Library Manager")

    # Add mode selection at the top
    mode = st.radio("Mode", ["Manual Entry", "Camera Capture"], horizontal=True)

    # Initialize session state
    if 'books_to_process' not in st.session_state:
        st.session_state.books_to_process = []
    if 'processed_books' not in st.session_state:
        st.session_state.processed_books = []
    if 'detected_books' not in st.session_state:
        st.session_state.detected_books = []
    if 'unprocessed_books' not in st.session_state:
        st.session_state.unprocessed_books = []

    if mode == "Manual Entry":
        # Book input form
        with st.form(key='add_book_form'):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Book Title", key="new_title")
            with col2:
                author = st.text_input("Author", key="new_author")
            col3, col4 = st.columns(2)
            with col3:
                submit_button = st.form_submit_button(label='Add Book')
            with col4:
                sample_button = st.form_submit_button(label='Load Sample Books')

        if submit_button and title:  # Only add if title is not empty
            add_book(title, author)
        if sample_button:
            load_sample_books()

    else:
        # Camera capture mode
        # Get API key
        api_key = st.text_input("Anthropic API Key", type="password")

        if api_key:
            img = camera_input()
            if img is not None:
                st.image(img)
                if st.button("Detect Books"):
                    detector = BookDetector(api_key)
                    results = detector.detect_books(img)

                    try:
                        st.session_state.detected_books = json.loads(results)['books']
                        st.json(results)  # Show the raw results
                    except json.JSONDecodeError:
                        st.error("Failed to parse detected books")

                # Only show add button if we have detected books
                if 'detected_books' in st.session_state and st.session_state.detected_books:
                    if st.button("Add Detected Books to Processing Queue"):
                        if 'books_to_process' not in st.session_state:
                            st.session_state.books_to_process = []
                        st.session_state.books_to_process.extend(st.session_state.detected_books)
                        st.success(f"Added {len(st.session_state.detected_books)} books to processing queue")
                        del st.session_state.detected_books

    # Process books section - moved outside mode selection
    if st.session_state.books_to_process:
        # Initialize our fetcher
        fetcher = BookMetadataFetcher()

        st.subheader("Books to Process")
        for idx, book in enumerate(st.session_state.books_to_process):
            st.write(f"### Book {idx + 1}: {book['title']} by {book['author']}")

            # Initialize search results for this book if needed
            results_key = f"results_{idx}"
            if results_key not in st.session_state:
                st.session_state[results_key] = fetcher.search_book(book["title"], book["author"])

            # Create selection options
            options = ["Select a book..."]
            options.extend([
                f"{result['volumeInfo']['title']} by {', '.join(result['volumeInfo'].get('authors', []))}"
                for result in st.session_state[results_key]
            ])

            # Selection dropdown
            selection = st.selectbox(
                "Choose the matching book:",
                options,
                key=f"selection_{idx}"
            )

            # Display selection
            if selection != "Select a book...":
                st.write(f"Selected: {selection}")

            st.markdown("---")  # Separator between books

        # Add a "Process Selections" button
        if st.button("Process All Selections"):
            # Process each selection
            unprocessed = []
            for idx, book in enumerate(st.session_state.books_to_process):
                selection_key = f"selection_{idx}"
                results_key = f"results_{idx}"

                if st.session_state[selection_key] == "Select a book...":
                    unprocessed.append(book)
                else:
                    # Find the selected result
                    selection = st.session_state[selection_key]
                    results = st.session_state[results_key]

                    # Find matching result
                    for result in results:
                        result_title = f"{result['volumeInfo']['title']} by {', '.join(result['volumeInfo'].get('authors', []))}"
                        if result_title == selection:
                            # Add to processed books
                            processed_book = fetcher.format_book_data(result)
                            st.session_state.processed_books.append(processed_book)
                            break

            # Store unprocessed books
            st.session_state.unprocessed_books = unprocessed

            # Clear books to process and their results
            for idx in range(len(st.session_state.books_to_process)):
                if f"results_{idx}" in st.session_state:
                    del st.session_state[f"results_{idx}"]
                if f"selection_{idx}" in st.session_state:
                    del st.session_state[f"selection_{idx}"]

            st.session_state.books_to_process = []

    # Display processed and unprocessed books
    if st.session_state.processed_books:
        st.subheader("Processed Books")
        for book in st.session_state.processed_books:
            st.write(f"✅ {book['title']} by {book['author']}")

        # Directly download CSV without separate button
        csv_data = "TITLE,AUTHOR (last, first),DATE,ISBN,PUBLICATION INFO,TAGS,RATING,REVIEW,DATE READ,PAGE COUNT,CALL NUMBER\n"

        for book in st.session_state.processed_books:
            # Handle author name formatting
            author_parts = book['author'].split(', ')
            if len(author_parts) == 1:
                author_parts = book['author'].split(' ')
            author = f"{author_parts[-1]}, {' '.join(author_parts[:-1])}"

            # Create publication info
            pub_info = f"{book['publisher']} ({book['publish_date']}), {book['number_of_pages']} pages"

            # Create CSV row
            row = [
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
            ]
            # Add escaped row to CSV data
            csv_data += ','.join(f'"{str(field)}"' for field in row) + '\n'

        st.download_button(
            label="Export to CSV",
            data=csv_data,
            file_name="library_thing_import.csv",
            mime="text/csv"
        )

    if st.session_state.unprocessed_books:
        st.subheader("Unprocessed Books")
        for book in st.session_state.unprocessed_books:
            st.write(f"❌ {book['title']} by {book['author']}")

if __name__ == "__main__":
    main()
