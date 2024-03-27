import os
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# BILLBOARD_ENDPOINT = f"{os.getenv('BILLBOARD_ENDPOINT')}"
BILLBOARD_ENDPOINT = "https://www.billboard.com/charts/hot-100/"
REDIRECT_URI = "http://example.com"
OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_ENDPOINT = "https://api.spotify.com/v1/search"

time_period = input("what year you would like to travel to? Type the date in  this format YYY-MM-DD: ")
year = time_period.split("-")[0]

def fetch_billboard_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for 4xx or 5xx status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error accessing Billboard website:", e)
        return None

web_data = fetch_billboard_data(f"{BILLBOARD_ENDPOINT}{time_period}/")
if web_data is None:
    exit(1)


# response = requests.get(f"{BILLBOARD_ENDPOINT}{time_period}/")
# web_data = response.text

# scarping billboard website
soup = BeautifulSoup(web_data, "html.parser")

songs = soup.find_all(name="h3", id="title-of-a-story", class_="u-line-height-125")
songs_list = [song.get_text().strip("\n\t") for song in songs]


artist_names = soup.find_all(name="span", class_="u-max-width-330")
artists_list = [artist.get_text().strip("\n\t") for artist in artist_names]

song_and_artist = dict(zip(songs_list, artists_list))
print(song_and_artist)


# authorizing spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope="playlist-modify-private",
        redirect_uri=REDIRECT_URI,
        show_dialog=True,
        cache_path="token.txt",
        username="sender send",
    )
)
user_id = sp.current_user()['id']

song_uris = []
# getting songs uri for songs in song_list by using song name only
# for song in songs_list:
#     # Search for the song and year
#     result = sp.search(q=f"track:{song} year:{year}", type="track")
#     # print(result)
#     try:
#         uri = result["tracks"]["items"][0]["uri"]
#         song_uris.append(uri)
#         # print(song_uris)
#     except IndexError:
#         print(f"{song} doesn't exist in Spotify. Skipped.")

# find songs uri by using song name  and artist name
for (song, artist) in song_and_artist.items():
    try:
        result = sp.search(q=f"track:{song} artist:{artist}", type="track")
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except:
        print(f"{song} doesn't exist in Spotify. Skipped.")

print(f"Number of songs found: {len(song_uris)}")


# creating private playlist
playlist = sp.user_playlist_create(name=f"top hit {time_period} Billboard-100", user=user_id, public=False,)
sp.playlist_add_items(playlist_id=playlist['id'], position=0, items=song_uris)




