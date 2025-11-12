# mistral_ocr/core.py
"""
Core backend logic for the Mistral OCR application.
Handles API interaction, image processing, and file operations.
"""

import base64
import os
import re
import time

# --- Configuration ---
MAX_WORKERS = 6  # Due to API rate limits, anything higher than 6 doesn't make a difference.
MAX_RETRIES = 10
RETRY_DELAY_SECONDS = 2
SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
PROCESSING_COLOR = 'gold'
PROCESSED_COLOR = 'green'
ERROR_COLOR = 'red3'
# --- End Configuration ---

# Read API key from environment variable
OCR_API_KEY = os.getenv("MISTRAL_API_KEY")

try:
    from mistralai import Mistral
except ImportError:
    Mistral = None

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise IOError(f"Error encoding image {os.path.basename(image_path)}: {e}")

def get_mime_type(file_path):
    """Determine the MIME type based on file extension."""
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower().lstrip('.')
    mime_types = {
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
        'gif': 'image/gif', 'bmp': 'image/bmp', 'tiff': 'image/tiff'
    }
    return mime_types.get(file_extension, 'image/jpeg')

def process_image_with_ocr(image_path, log_queue, cancel_event):
    """
    Process a single image with Mistral OCR API, with retry logic.
    Sends status updates to the GUI via the log_queue.
    """
    log_queue.put(('status_update', image_path, 'processing'))
    if cancel_event.is_set():
        return

    for attempt in range(1, MAX_RETRIES + 1):
        if cancel_event.is_set():
            return

        try:
            base_dir = os.path.dirname(image_path)
            base_filename = os.path.splitext(os.path.basename(image_path))[0]
            markdown_file = os.path.join(base_dir, f"{base_filename}_OCR.md")

            base64_image = encode_image(image_path)
            if not base64_image:
                raise ValueError("Failed to encode image to base64.")

            if cancel_event.is_set():
                return
            
            if Mistral is None:
                raise ImportError("Mistral AI client is not installed.")
            if not OCR_API_KEY:
                raise ValueError("MISTRAL_API_KEY is not set.")

            client = Mistral(api_key=OCR_API_KEY)
            mime_type = get_mime_type(image_path)
            
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={"type": "image_url", "image_url": f"data:{mime_type};base64,{base64_image}"}
            )
            
            if cancel_event.is_set():
                return

            extracted_markdown = ""
            if hasattr(ocr_response, 'pages') and ocr_response.pages:
                for page in ocr_response.pages:
                    if hasattr(page, 'markdown'):
                        extracted_markdown += page.markdown + "\n\n"
            elif hasattr(ocr_response, 'text'):
                extracted_markdown = ocr_response.text
            else:
                extracted_markdown = str(ocr_response)

            final_markdown = re.sub(r'!\[.*?\]\(.*?\)', '', extracted_markdown).strip()
            
            with open(markdown_file, "w", encoding="utf-8") as f:
                f.write(final_markdown)

            log_queue.put(('status_update', image_path, 'success'))
            return markdown_file # Success, return the path of the created file

        except Exception as e:
            if cancel_event.is_set():
                return
    
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                log_queue.put(('status_update', image_path, 'error'))
                return None