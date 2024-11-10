import anthropic
import streamlit as st
from PIL import Image
import io
import base64
import json
from datetime import datetime

class BookDetector:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def detect_books(self, image_data):
        """Process image with Claude API and log progress"""
        # Convert streamlit image to base64
        bytes_data = image_data.getvalue()
        base64_image = base64.b64encode(bytes_data).decode()

        send_time = datetime.now()
        st.write("Starting API call...")

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image and identify any visible book titles and authors.
                            Return the results in this exact JSON format:
                            {
                                "books": [
                                    {"title": "Book Title", "author": "Author Name"},
                                    ...
                                ]
                            }
                            If no books are detected, return an empty books array.
                            Only return the JSON, no other text."""
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }]
            )

            receive_time = datetime.now()
            processing_time = (receive_time - send_time).total_seconds()

            result = response.content[0].text

            # Parse result to get book count
            try:
                parsed_result = json.loads(result)
                current_books = parsed_result.get('books', [])
                book_count = len(current_books)
                first_title = current_books[0]['title'] if current_books else "None"

                log_message = (
                    f"\nAPI Transaction: {send_time.strftime('%H:%M:%S.%f')[:-4]} → "
                    f"{receive_time.strftime('%H:%M:%S.%f')[:-4]} "
                    f"({processing_time:.2f}s)\n"
                    f"Detections: {book_count} | "
                    f"First: {first_title}"
                )
                st.write(log_message)
            except json.JSONDecodeError:
                st.error(f"Error parsing JSON response: {result}")

            return result

        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return '{"books": []}'
