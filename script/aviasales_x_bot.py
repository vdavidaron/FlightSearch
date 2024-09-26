import urllib.parse
import requests
import json
import os
import random
import schedule
import time
from requests_oauthlib import OAuth1Session
from datetime import datetime


# Path to the JSON file
keys_file = 'api_keys.json'

# Read the JSON file and load the content
with open(keys_file, 'r') as file:
    keys = json.load(file)
    print("file read")

# Access the key
tp_aviasales_key = keys['tp_aviasales_key']
#tp_aviasales_key = os.environ.get('TP_API_TOKEN')

unsplash_access_key = keys['unsplash_access_key']

url = "https://api.travelpayouts.com/aviasales/v3/get_special_offers"
europe_airports = ['LON', 'CDG', 'AMS', 'FRA', 'MAD', 'BCN', 'MXP', 'FCO', 'VIE', 'DUB', 'BUD', 'BTS']

headers = {'x-access-token': tp_aviasales_key}

def get_params(origin):
    return {'origin': origin, 'currency': 'eur'}

def fetch_special_offers():
    global special_offers
    special_offers = []
    for origin in europe_airports:
        params = get_params(origin)
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                special_offers.extend(data['data'])
    print("Special offers refreshed.")

def convert_link(original_link):
    base_new_link = "https://tp.media/r"
    params = {
        "marker": "558858",
        "trs": "334726",
        "p": "4114",
        "u": urllib.parse.quote(original_link, safe=''),
        "campaign_id": "100"
    }
    new_link = f"{base_new_link}?{urllib.parse.urlencode(params)}"
    return new_link

def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except ValueError:
        return date_str
    
def generate_hashtags(offer):
    hashtags = [
        f"#{offer['origin_name_declined']}",
        f"#{offer['destination_name_declined']}",
        "#FlightDeals",
        "#Travel",
        "#CheapFlights"
    ]
    return " ".join(hashtags)

def search_image(query):
    search_url = f"https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {unsplash_access_key}"}
    params = {"query": query, "per_page": 1}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    if search_results["results"]:
        return search_results["results"][0]["urls"]["regular"]
    return None

def post_tweet():
    if not special_offers:
        print("No special offers available to tweet.")
        return

    selected_offer = None
    for _ in range(len(special_offers)):
        offer = random.choice(special_offers)
        if offer["link"] not in posted_offers:
            selected_offer = offer
            break

    if not selected_offer:
        print("No new offers to post.")
        return

    original_link = "https://www.aviasales.com" + selected_offer["link"]
    new_link = convert_link(original_link)
    departure_date = format_date(selected_offer['departure_at'])
    hashtags = generate_hashtags(selected_offer)

    tweet_text = (
        f"{selected_offer['title']} "
        f"starting at just {selected_offer['price']} euros, with an example departure date of "
        f"{departure_date}.\n\n{new_link}\n\n{hashtags}"
    )

    city_image_url = search_image(selected_offer['destination_name'])
    if not city_image_url:
        print(f"No image found for destination: {selected_offer['destination_name']}")
        return

    # Download the image
    image_response = requests.get(city_image_url)
    if image_response.status_code != 200:
        print(f"Failed to download image: {city_image_url}")
        return

    image_path = 'destination_image.jpg'
    with open(image_path, 'wb') as f:
        f.write(image_response.content)


    consumer_key = keys['consumer_key']
    consumer_secret = keys['consumer_secret']
    #consumer_key = os.environ.get('CONSUMER_KEY')
    #consumer_secret = os.environ.get('CONSUMER_SECRET')
    tokens_file = 'twitter_tokens.json'

    def save_tokens(tokens):
        with open(tokens_file, 'w') as f:
            json.dump(tokens, f)

    def load_tokens():
        with open(tokens_file, 'r') as f:
            return json.load(f)

    def get_access_tokens():
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
        fetch_response = oauth.fetch_request_token(request_token_url)
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print(f"Please go here and authorize: {authorization_url}")
        verifier = input("Paste the PIN here: ")
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)
        save_tokens(oauth_tokens)
        return oauth_tokens

    if os.path.exists(tokens_file):
        oauth_tokens = load_tokens()
    else:
        oauth_tokens = get_access_tokens()

    access_token = oauth_tokens.get("oauth_token")
    access_token_secret = oauth_tokens.get("oauth_token_secret")

    if not access_token or not access_token_secret:
        raise ValueError("Access tokens are missing")

    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    
    
    # Upload the image to Twitter
    media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"
    with open(image_path, 'rb') as f:
        files = {'media': f}
        media_response = oauth.post(media_upload_url, files=files)

    if media_response.status_code != 200:
        raise Exception(f"Image upload failed: {media_response.status_code} {media_response.text}")

    media_id = media_response.json()['media_id_string']


    payload = {
        "text": tweet_text,
        "media": {
            "media_ids": [media_id]
        }
    }
    response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

    if response.status_code != 201:
        raise Exception(f"Request returned an error: {response.status_code} {response.text}")

    print(f"Tweet posted: {tweet_text}")

    posted_offers.add(selected_offer["link"])

# Schedule tasks
schedule.every(3).hours.do(fetch_special_offers)
schedule.every(1).minute.do(post_tweet)

# Initial fetch of special offers
fetch_special_offers()

# Set to keep track of posted offers
posted_offers = set()

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
