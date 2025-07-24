import asyncio
import os
from ddgimage import Client, DDGSearchException

# --- Configuration ---
# You can change these values to test different scenarios
SEARCH_QUERY = "Red Panda"  # The search term for images
MAX_IMAGES_TO_DOWNLOAD = 10 # Maximum number of images to download  
OUTPUT_DIR = "image_downloads"  # Directory to save downloaded images
MIN_PIXELS = 1_000_000  # 1 Megapixel

async def main():
    """
    An asynchronous function to test the ddgimage library.
    It searches for images with Safe Search Moderate and downloads only those
    that are larger than 1 megapixel.
    """
    print(f"--- Starting Image Downloader Test ---")
    print(f"Search Query: '{SEARCH_QUERY}'")
    print(f"Max Downloads: {MAX_IMAGES_TO_DOWNLOAD}")
    print(f"Output Directory: '{OUTPUT_DIR}'")
    print(f"Minimum Resolution: {MIN_PIXELS / 1_000_000} Megapixel(s)")
    print("-" * 40)

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Instantiate the client
    client = Client()
    downloaded_count = 0

    try:
        # Use an async for loop to iterate through the search results
        # NEW: Added safesearch="off" to the function call
        async for result in client.asearch(SEARCH_QUERY, safesearch="-1"): # Search with Safe Search ("on": "1", "moderate": "-1", "off": "-2")
            if downloaded_count >= MAX_IMAGES_TO_DOWNLOAD:
                print("\nReached the desired number of downloads. Stopping.")
                break

            print(f"\nFound Image: '{result.title}'")
            print(f"  Dimensions: {result.width}x{result.height}")

            # NEW: Check if the image meets the minimum resolution requirement
            total_pixels = result.width * result.height
            if total_pixels < MIN_PIXELS:
                print(f"  -> Skipping: Image is smaller than {MIN_PIXELS / 1_000_000}MP.")
                continue

            print(f"  Source URL: {result.image_url}")

            try:
                # Attempt to download the image
                print(f"-> Attempting to download...")
                await client.download(str(result.image_url), OUTPUT_DIR)
                downloaded_count += 1
                print(f"-> Success! Downloaded to '{OUTPUT_DIR}'. ({downloaded_count}/{MAX_IMAGES_TO_DOWNLOAD})")

            except DDGSearchException as e:
                # Handle potential download errors gracefully
                print(f"-> Download failed. Error: {e}")
            except Exception as e:
                print(f"-> An unexpected error occurred during download: {e}")

    except DDGSearchException as e:
        print(f"\nAn error occurred during the search: {e}")
    except Exception as e:
        print(f"\nAn unexpected and critical error occurred: {e}")

    print("-" * 40)
    print(f"--- Test Complete. Total images downloaded: {downloaded_count} ---")


if __name__ == "__main__":
    # This is the standard way to run an async main function
    asyncio.run(main())