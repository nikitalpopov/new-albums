import discogs_client
import musicbrainzngs
import pandas
import pylast
from pprint import pprint

# last.fm
api_key = '0d2c6862c7279e31682eace2808e3911'
api_secret = 'f2dd5b521da5f6dbf4ae1835dc96193e'
username = 'tapochek97'
password_hash = pylast.md5('')  # @todo fill password

# musicbrainz
musicbrainzngs.set_useragent("new-albums", "0.0.1", "https://github.com/nikitalpopov/new-albums")

# discogs
discogs = discogs_client.Client('new-albums/0.0.1', user_token='tnKwPJHZUkDdOTwQWdLRZEYWziNRQhBoKnLjDumm')

# run script
api = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret, username=username)
artists = pylast.User(username, api).get_library().get_artists(limit=None)

discogs_id = []
musicbrainz_id = []
for artist in artists:
    if artist.playcount >= 20:
        musicbrainz_search = musicbrainzngs.search_artists(artist=artist.item.name)['artist-list']
        discogs_search = discogs.search(artist.item.name, type='artist')
        if musicbrainz_search:
            musicbrainz_id.append(musicbrainz_search[0]['id'])
        else:
            musicbrainz_id.append(None)
        if discogs_search:
            discogs_id.append(discogs_search[0].id)
        else:
            discogs_id.append(None)
    else:
        musicbrainz_id.append(None)
        discogs_id.append(None)

data = {'artist': [artist.item.name for artist in artists], 'musicbrainz_id': musicbrainz_id, 'discogs_id': discogs_id}
dataframe = pandas.DataFrame.from_dict(data).dropna(how='any')
dataframe.to_csv('library.csv', sep=',', encoding='utf-8')
# pprint(dataframe)
# musicbrainzngs.get_artist_by_id(artist_id, includes=["release-groups"], release_type=["album", "ep"])
