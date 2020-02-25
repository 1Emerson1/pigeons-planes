import requests
import re
import bs4
import yaml
import spotipy
import spotipy.util as util
from pprint import pprint

re_title = re.compile(r'(.+-?.+)\s?[\[|\(|\/]')
re_title2 = re.compile(r'(.+-?.+)\s?[\[|\(|\/]\s')
re_extras = re.compile(r'ft|ft.|feat|featuring|music|film|movie|audio|official|video|[(]|[)]|\[|\]|\|')
re_yt = re.compile(r'"https:\\\\u002F\\\\u002Fwww.youtube.com\\\\u002Fembed\\\\u002F(.{11})\\\\\\?"')
re_sc = re.compile(r'tracks\\\\u002F(.+)&amp;color')

YOUTUBE = 'https://www.youtube.com/watch?v='
SOUNDCLOUD = 'https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/'
NOEMBED = 'https://noembed.com/embed?url='

def load_config():
    global user_config
    stream = open('config.yaml')
    user_config = yaml.load(stream)
    pprint(user_config)

def find_youtube(html_contents):
    # searching for youtube ids
    print('Searching for YouTube IDs...')
    yt_id = re_yt.findall(html_contents)
    print('Found %s YouTube IDs' % len(yt_id))

    return yt_id

def find_soundcloud(html_contents):
    # searching for soundcloud track ids
    print('Searching for soundcloud track IDS...')
    sc_id = re_sc.findall(html_contents)

    return sc_id

# uses oembed service to get link info
def get_title(link):
    # request json
    response = requests.get(link)
    response = response.json()

    title = response['title'].lower()

    return title

def convert_playlist(web):
    # request url and get htm contents
    url = requests.get(web)
    html_contents = url.text

    sc_id = find_soundcloud(html_contents)
    yt_id = find_youtube(html_contents)

    titles = []

    # extract soundcloud link and get track info from oembed
    if(len(sc_id) > 0):
        for id in sc_id:
            sc_contents = requests.get(SOUNDCLOUD+id).text
            sc_links = re.findall(r'<link rel="canonical" href="(.+)"><title', sc_contents)
        print('Found %s Soundcloud track IDs' % len(sc_id))

        # cleaning up sc track names
        for link in sc_links:
            link = NOEMBED+link

            title = get_title(link)
            
            if(re_title.match(title)):
                title = re_title.match(title)[0]

            title = re_extras.sub('', title)

            titles.append(title)
    else:
        print('No soundcloud track IDs found.')

    # extracting youtube link and get track info from oembed
    if(len(yt_id) > 0):
        
        for id in yt_id:
            link = NOEMBED+YOUTUBE+id
            title = get_title(link)

            if(re_title.match(title)):
                title = re_title.match(title)[0]
            if(re_title2.match(title)):
                title = re_title2.match(title)[0]

            title = re_extras.sub('', title)

            titles.append(title)
    else:
        print('No youtube IDS found.')

    print("Total songs found: ", len(titles))

    spotify_ids = search_spotify(titles)

    # gathering playlist info
    playlist_description = re.findall(r'"description":\s?"(.+)"', html_contents)[0]
    date_published = re.findall(r'"datePublished":\s?"([0-9]{4}-[0-9]{2}-[0-9]{2})', html_contents)[0]
    playlist_name = "Pigeons & Planes - " + date_published

    # creating playlist
    playlist_id = create_playlist(playlist_name, playlist_description)

    add_to_playlist(playlist_id, spotify_ids)

def search_spotify(titles):
    # searching for track in spotify
    print ('Searching for track on spotify')
    spotify_ids = []
    for title in titles:
        song_results = sp.search(q=title, type='track', limit=1)

        lost_count = 0
        try:
            spotify_id = song_results['tracks']['items'][0]['id']
            spotify_ids.append(spotify_id)
        except IndexError:
            lost_count = lost_count+1 

    print("Spotify track IDs found: ", len(spotify_ids))
    print("Spotify tracks IDs not found: ", lost_count)

    return spotify_ids

def create_playlist(playlist_name, playlist_description):
    global sp
    global user_config

    print('Creating spotify playlist')
    playlist = sp.user_playlist_create(user_config['username'], playlist_name, description=playlist_description)

    playlist_id = playlist['id']

    return playlist_id

def add_to_playlist(playlist_id, spotify_ids):
    global sp
    global user_config

    try:
        # adding songs to playlist
        print('Adding songs to playlist')
        sp.user_playlist_add_tracks(user_config['username'], playlist_id=playlist_id, tracks=spotify_ids)
    except:
        print('Adding tracks failed!')

if __name__ == '__main__':
    global sp
    global user_config
    load_config()

    WEB = 'https://www.complex.com/pigeons-and-planes/2020/01/the-rotation-january-2020/beam-95'

    # spotify credentials
    token = util.prompt_for_user_token(user_config['username'], scope='playlist-modify-public', client_id=user_config['client_id'], client_secret=user_config['client_secret'], redirect_uri=user_config['redirect_uri'])

    if token:
        sp = spotipy.Spotify(auth=token)
        convert_playlist(WEB)

        print("All done!")
    else:
        print ('Cannot get token for', user_config['username'])