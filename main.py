import discogs_client
import json
import lxml.html
import musicbrainzngs
import pandas
import pylast
import requests
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


def extract(el, css_sel):
    ms = el.cssselect(css_sel)
    return None if len(ms) != 1 else ms[0].text


def get_albums(artist_id):
    url = "http://www.discogs.com/artist/" + str(artist_id) + "?limit=500"
    r = requests.get(url, headers={'User-Agent': 'I wish your API was better?'})
    root = lxml.html.fromstring(r.text)
    albums = []

    for row in root.cssselect("#artist tr"):
        section = extract(row, "td h3")
        if section is not None:
            if section == "Albums":
                continue
            if section == "Singles & EPs":
                break

        id = row.get("data-object-id")
        type = row.get("data-object-type")
        title = extract(row, ".title a")
        formats = extract(row, ".title .format")
        # todo full release date
        year = extract(row, "td[data-header=\"Year: \"]")
        if formats is not None:
            if 'album' in formats.lower():
                albums.append((id, title, year))

    return albums


# run script
api = pylast.LastFMNetwork(api_key=api_key,
                           api_secret=api_secret,
                           username=username)
artists = pylast.User(username, api).get_library().get_artists(limit=None)

artists = [artist.item.name for artist in artists if artist.playcount >= 20]
discogs_id = []
musicbrainz_id = []
discography = []
for artist in artists:
    # print(artist)
    try:
        musicbrainz_search = musicbrainzngs.search_artists(artist=artist)['artist-list']
    except:
        musicbrainz_id.append(None)
    else:
        if musicbrainz_search:
            musicbrainz_id.append(musicbrainz_search[0]['id'])

            releases = musicbrainzngs.get_artist_by_id(musicbrainz_id[-1],
                                                       includes=["release-groups"],
                                                       release_type=["album", "ep"])['artist']['release-group-list']
            albums = []
            for release in releases:
                try:
                    release['type']
                except KeyError:
                    continue
                else:
                    if release['type'] == 'Album':
                        albums.append((release['id'], release['title'], release['first-release-date']))
            discography.append(albums)
        else:
            discography.append(None)
            musicbrainz_id.append(None)

    try:
        discogs_search = discogs.search(artist, type='artist')
    except:
        print('some error with discogs')
        discogs_id.append(None)
    else:
        if discogs_search:
            discogs_id.append(str(discogs_search[0].id))

            albums = get_albums(discogs_id[-1])
            if discography[-1]:
                continue
            else:
                discography[-1] = albums
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

data = {'artist': artists,
        'musicbrainz_id': musicbrainz_id,
        'discogs_id': discogs_id,
        'discography': discography}  # discography can contain either musicbrainz or discogs ids
dataframe = pandas.DataFrame.from_dict(data)
dataframe.to_csv('library.csv', sep=',', encoding='utf-8')
