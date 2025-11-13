import requests
import sys

# --- Configuration ---
# IMPORTANT: Replace this with your actual GIPHY API Key
# You can use the general 'GIPHY SDK Key' (often 'dc6zaTOxFJmzC') for testing, 
# but a personalized Beta Key is recommended.
API_KEY = "YOUR_GIPHY_API_KEY"
# ---------------------

def giphy_search(keyword, num_results=10,_key):
    """
    Searches GIPHY for GIFs matching the keyword and prints the results
    to the console in a numbered, field-separated format.
    """
    try:
        # GIPHY Search API endpoint
        url = "https://api.giphy.com/v1/gifs/search"
        
        # API request parameters
        params = {
            'api_key': _key,
            'q': keyword,
            'limit': num_results,
            'rating': 'g', # Restrict to 'G' rated content
            'lang': 'en'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()

        if 'data' not in data or not data['data']:
            print(f"No GIFs found for '{keyword}'.")
            return

        gifs = data['data']
        
        print(f"Displaying first {len(gifs)} results:")
        print("=" * 30)
        
        # Iterate over the results and print them in the requested format
        for i, gif in enumerate(gifs):
            # The GIPHY API provides a 'url' (GIPHY page) and 'images' (direct file links)
            
            # 1. Numbered List and Title Field
            print(f"\n{i+1}. 🖼️ Title/Slug: **{gif.get('title', 'No Title')} / {gif.get('slug', 'N/A')}**")
            
            # 2. Item info separated by fields
            print(f"   GIF ID: {gif.get('id', 'N/A')}")
            print(f"   Username: {gif.get('username', 'Anonymous') if gif.get('username') else 'Anonymous'}")
            print(f"   Imported: {gif.get('import_datetime', 'N/A')}")
            
            # Direct link to the image file (using a standard medium size)
            if 'images' in gif and 'original' in gif['images']:
                print(f"   Direct URL: {gif['images']['original']['url']}")
            else:
                print(f"   GIPHY Page: {gif.get('url', 'N/A')}")


    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the API request. Check your key or connection: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

def google_image_search(keyword, num_results=10,_key):
    try:
        # Google Custom Search API endpoint
        url = "https://www.googleapis.com/customsearch/v1"
        
        # API request parameters
        params = {
            'key': _key,
            'cx': CX,
            'q': keyword,
            'searchType': 'image', # Essential parameter for image search
            'num': num_results
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()

        if 'items' not in data:
            # The 'items' key is missing if no results are found
            print(f"No image results found for '{keyword}'.")
            return

        photos = data['items']
        
        print(f"Displaying first {len(photos)} results:")
        print("=" * 30)
        
        # Iterate over the results and print them in the requested format
        for i, item in enumerate(photos):
            image_info = item.get('image', {})
            
            # 1. Numbered List and Title Field
            print(f"\n{i+1}. 🖼️ Source Title: **{item.get('title', 'No Title')}**")
            
            # 2. Item info separated by fields
            print(f"   Image URL: {item.get('link', 'N/A')}")
            print(f"   Context Page: {image_info.get('contextLink', 'N/A')}")
            print(f"   Dimensions: {image_info.get('width', 'N/A')}px x {image_info.get('height', 'N/A')}px")
            print(f"   File Size: {image_info.get('byteSize', 'N/A')} bytes")

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the API request. Check your key/CX or connection: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
