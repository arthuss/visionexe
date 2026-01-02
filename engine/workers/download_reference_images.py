import os
import json
import urllib.request
import urllib.parse
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_DIR = "reference_images"
API_URL = "https://commons.wikimedia.org/w/api.php"

LOCATIONS = {
    "Etappe_1/Mount_Sinai": "Mount Sinai landscape",
    "Etappe_1/Negev_Desert": "Makhtesh Ramon landscape",
    "Etappe_1/Judean_Mountains": "Judean Mountains landscape",
    "Etappe_1/Qumran_Caves": "Qumran caves landscape",
    "Etappe_1/Tel_Dan": "Tel Dan nature reserve spring",
    "Etappe_1/Mount_Hermon": "Mount Hermon landscape",
    "Etappe_2/Jordan_Rift_Valley": "Jordan Rift Valley landscape",
    "Etappe_2/Dallol_Ethiopia": "Dallol hydrothermal",
    "Etappe_2/Simien_Mountains": "Simien Mountains landscape",
    "Etappe_3/Indian_Ocean_Coast": "Socotra coast",
    "Etappe_3/Socotra_Island": "Socotra Dragon Blood Tree",
    "Etappe_3/Svalbard": "Svalbard mountains",
    "Etappe_4/Wadi_Rum": "Wadi Rum desert",
    "Etappe_4/Jerusalem_Kidron": "Kidron Valley",
    "Etappe_4/Jerusalem_Gehenna": "Hinnom Valley nature",
    "Etappe_3/Atmospheric_IO_Gates": "Richat Structure",
    "Etappe_2/Core_Cluster_Mountains": "Rainbow Mountain Vinicunca",
    "Etappe_2/Root_Mainframe_Hall": "Naica Mine crystals"
}

def get_image_urls(search_term, limit=5):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": 6,  # File namespace
        "gsrsearch": search_term,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|mime",
    }
    
    url = API_URL + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Bot/1.0 (mailto:bot@example.com)'
            }
        )
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            
        urls = []
        if "query" in data and "pages" in data["query"]:
            for page_id, page_info in data["query"]["pages"].items():
                if "imageinfo" in page_info:
                    for info in page_info["imageinfo"]:
                        if info["mime"] in ["image/jpeg", "image/png"]:
                            urls.append(info["url"])
        return urls
    except Exception as e:
        print(f"Error searching for {search_term}: {e}")
        return []

def download_image(url, folder, index):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename = f"image_{index+1}.jpg"
    filepath = os.path.join(folder, filename)
    
    try:
        print(f"Downloading {url} to {filepath}...")
        # Add User-Agent to avoid 403 Forbidden
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        )
        with urllib.request.urlopen(req, context=ctx) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
        print("Done.")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        
    for folder_suffix, search_term in LOCATIONS.items():
        folder_path = os.path.join(BASE_DIR, folder_suffix)
        print(f"Processing {search_term} -> {folder_path}")
        
        urls = get_image_urls(search_term)
        if not urls:
            print(f"No images found for {search_term}")
            continue
            
        for i, url in enumerate(urls):
            download_image(url, folder_path, i)

if __name__ == "__main__":
    main()
