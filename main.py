import discogs_client
import json
import musicbrainzngs
import pandas
import pygn
import pylast
import requests
import spotipy
from datetime import datetime
from pprint import pprint

# last.fm
api_key = '0d2c6862c7279e31682eace2808e3911'
api_secret = 'f2dd5b521da5f6dbf4ae1835dc96193e'
username = 'tapochek97'
password_hash = pylast.md5('')  # @todo fill password

# musicbrainz
musicbrainzngs.set_useragent("new-albums", "0.0.1", "https://github.com/nikitalpopov/new-albums")

# discogs
user_token = 'tnKwPJHZUkDdOTwQWdLRZEYWziNRQhBoKnLjDumm'
discogs = discogs_client.Client('new-albums/0.0.1', user_token=user_token)

# spotify
spotify = spotipy.Spotify()

# gracenote
gracenote_client = ''
gracenote_id = ''

# run script
api = pylast.LastFMNetwork(api_key=api_key,
                           api_secret=api_secret,
                           username=username)
artists = pylast.User(username, api).get_library().get_artists(limit=None)

artists = [artist.item.name for artist in artists if artist.playcount >= 20]
discogs_id = []
musicbrainz_id = []
spotify_id = []
discography = []
for artist in artists:
    print(artist)
    try:
        musicbrainz_search = musicbrainzngs.search_artists(artist=artist)['artist-list']

        if musicbrainz_search:
            musicbrainz_id.append(musicbrainz_search[0]['id'])

            # get albums
            # pprint(musicbrainzngs.get_artist_by_id(musicbrainz_search[0]['id'],
            #                                        includes=["release-groups"],
            #                                        release_type=["album", "ep"])['artist']['release-group-list'])
        else:
            musicbrainz_id.append(None)
    except:
        musicbrainz_id.append(None)

    try:
        discogs_search = discogs.search(artist, type='artist')

        if discogs_search:
            discogs_id.append(str(discogs_search[0].id))

            # get albums
            # releases = requests.get('https://api.discogs.com/artists/' + discogs_id[-1] + '/releases'
            #                         + '?sort=year'
            #                         + '&sort_order=desc')
            # pprint(releases.json()['releases'])
            # print()
            # releases = requests.get('https://api.discogs.com/database/search'
            #                         + '?artist=' + artist
            #                         + '&year=' + str(datetime.now().year - 1)
            #                         + '&format=album'
            #                         + '&type=release'
            #                         + '&token=' + user_token)
            # pprint(releases.json()['results'])
            # for release in discogs_search[0].releases:
            #     pprint(release)
        else:
            discogs_id.append(None)
    except:
        discogs_id.append(None)

    try:
        spotify_search = spotify.search(q='artist:' + artist, type='artist')

        if spotify_search:
            spotify_id.append(spotify_search['artists']['items'][0]['id'])

            # get albums
            # albums = []
            # results = spotify.artist_albums(spotify_id[-1], album_type='album')
            # albums.extend(results['items'])
            # while results['next']:
            #     results = spotify.next(results)
            #     albums.extend(results['items'])
            # seen = set()  # to avoid dups
            # albums.sort(key=lambda album: album['name'].lower())
            # for album in albums:
            #     name = album['name']
            #     if name not in seen:
            #         print((' ' + name))
            #         seen.add(name)
        else:
            spotify_id.append(None)
    except:
        spotify_id.append(None)

    try:
        # gracenote = pygn.get_discography(clientID=gracenote_client, userID=gracenote_id, artist=artist)
        # discography.append(json.dumps(discography, sort_keys=True, indent=4))
        # for release in discography[-1]:
        #     print(release['album_year'] + ' ' + release['album_title'])
        discography.append(None)
    except:
        discography.append(None)

data = {'artist': artists,
        'musicbrainz_id': musicbrainz_id,
        'discogs_id': discogs_id,
        'spotify_id': spotify_id,
        'discography': discography}
dataframe = pandas.DataFrame.from_dict(data)
dataframe.to_csv('library.csv', sep=',', encoding='utf-8')

# musicbrainzngs.get_artist_by_id(artist_id, includes=["release-groups"], release_type=["album", "ep"])
