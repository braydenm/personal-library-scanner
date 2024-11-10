# Personal Library Scanner

Built because manual data entry for keeping track of books sucks.

## What it does
- Scans books with your camera using Claude's vision API
- Fetches proper metadata from Google Books
- Exports everything in LibraryThing format
- No more typing ISBNs like it's 1999

## Setup
1. Clone this repo
2. `pip install -r requirements.txt`
3. Get your API keys (Anthropic & Google Books)
4. `streamlit run src/personal_library/app.py`

## Features
- Camera scanning (when you can)
- Manual entry (when you can't)
- Book metadata verification
- CSV export that actually works with LibraryThing

## Why?
Because life's too short to manually catalog your library. This tool does the heavy lifting so you can spend more time reading and less time cataloging.

Built with Streamlit, Claude API, and Zed.
