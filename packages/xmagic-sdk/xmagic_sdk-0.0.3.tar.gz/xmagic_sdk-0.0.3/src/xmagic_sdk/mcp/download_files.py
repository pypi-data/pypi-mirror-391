from typing import Dict, List
import os
import tempfile
import uuid
import urllib.parse
import requests
from xmagic_sdk.logging.logging import configure_logger

logger = configure_logger(__name__)


def download_files_from_presigned_urls(
    files_or_images: Dict[str, str],
):
    urls = [url for url in files_or_images.values()]

    unique_dirname = f"downloads_{uuid.uuid4().hex[:8]}"
    temp_dir = os.path.join(tempfile.gettempdir(), unique_dirname)
    os.makedirs(temp_dir, exist_ok=True)

    downloaded_files = []

    for i, url in enumerate(urls):
        try:
            # Parse the URL to extract potential filename
            parsed_url = urllib.parse.urlparse(url)
            path = parsed_url.path

            # Extract filename from the path
            filename = os.path.basename(path)

            # Handle URLs without a clear filename
            if not filename or filename == "":
                # Try to get filename from content-disposition header
                try:
                    # Just do a HEAD request to get headers
                    response = requests.head(url, allow_redirects=True, timeout=10)
                    if "content-disposition" in response.headers:
                        import re

                        content_disp = response.headers["content-disposition"]
                        match = re.findall('filename="?([^"]+)"?', content_disp)
                        if match:
                            filename = match[0]
                except Exception as e:
                    print(f"Warning: Could not get headers from {url}: {e}")

            # If still no filename, create a unique one
            if not filename or filename == "":
                # Try to get extension from 'response-content-type' in query params
                params = urllib.parse.parse_qs(parsed_url.query)
                content_type = params.get("response-content-type", [""])[0]
                extension = ""

                if content_type:
                    if "pdf" in content_type:
                        extension = ".pdf"
                    elif "jpeg" in content_type or "jpg" in content_type:
                        extension = ".jpg"
                    elif "png" in content_type:
                        extension = ".png"
                    elif "zip" in content_type:
                        extension = ".zip"
                    elif "text" in content_type:
                        extension = ".txt"

                filename = f"file_{uuid.uuid4().hex[:8]}{extension}"

            if (
                filename is not None
                and isinstance(filename, str)
                and len(filename) > 25
            ):
                filename = filename[25:]

            # Create full path for the file
            file_path = os.path.join(temp_dir, filename)

            # Download the file - don't modify the presigned URL
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            downloaded_files.append(file_path)
            logger.info(f"Downloaded: {filename} -> {file_path}")

        except Exception as e:
            logger.error(f"Failed to download URL #{i+1}: {e}")

    return temp_dir, downloaded_files
