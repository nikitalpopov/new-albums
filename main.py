import discogs_client
import json
import lxml.html
import musicbrainzngs
import pandas
import pylast
import requests
from colored import fg, attr
from datetime import datetime
from operator import itemgetter
from pprint import pprint

# last.fm
api_key = '0d2c6862c7279e31682eace2808e3911'
api_secret = 'f2dd5b521da5f6dbf4ae1835dc96193e'
username = 'tapochek97'
password_hash = pylast.md5('')  # @todo fill password


def get_artists(plays=20):
    api = pylast.LastFMNetwork(api_key=api_key,
                               api_secret=api_secret,
                               username=username)

    artists = [artist.item.name for artist in pylast.User(username, api).get_library().get_artists(limit=None)
               if artist.playcount >= plays]
    with open('artists.txt', 'w') as file:
        for artist in artists:
            file.write("%s\n" % artist)
        file.close()

    return artists


# musicbrainz
musicbrainzngs.set_useragent("new-albums", "0.0.1", "https://github.com/nikitalpopov/new-albums")


def get_albums_from_musicbrainz(musicbrainz):
    albums = []
    for release in \
            musicbrainzngs.get_artist_by_id(musicbrainz, includes=["release-groups"],
                                            release_type=["album", "ep"])['artist']['release-group-list']:
        try:
            release['type']
        except KeyError:
            continue
        else:
            if release['type'] == 'Album':
                albums.append({'id': release['id'],
                               'title': release['title'],
                               'date': release['first-release-date']})
    for album in albums:
        try:
            album['date'] = datetime(*[int(x) for x in album['date'].split('-')
                                       + [1] * (3 - len(album['date'].split('-')))])
        except:
            album['date'] = datetime(1000, 1, 1)
        # print(album['title'] + ': ', album['date'])
        # album['date'] = datetime.strptime(album['date'], '%Y-%m-%d')
    return sorted(albums, key=itemgetter('date'), reverse=True)


# discogs
user_token = 'tnKwPJHZUkDdOTwQWdLRZEYWziNRQhBoKnLjDumm'
discogs_cli = discogs_client.Client('new-albums/0.0.1', user_token=user_token)


def extract(el, css_sel):
    ms = el.cssselect(css_sel)
    return None if len(ms) != 1 else ms[0].text


def get_albums_from_discogs(artist_id):
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
        year = extract(row, "td[data-header=\"Year: \"]")
        try:
            date = datetime(int(year), 1, 1)
        except:
            date = datetime(1000, 1, 1)
        if formats is not None:
            if 'album' in formats.lower():
                albums.append({'id': id, 'title': title, 'date': date})
        albums = sorted(albums, key=itemgetter('date'), reverse=True)

    return albums


# run script
artists = get_artists()
musicbrainz_id = []
discogs_id = []
discography = []
for artist in artists:
    print(fg(2) + artist + attr(0))
    musicbrainz = None
    discogs = None
    releases = {'musicbrainz': None, 'discogs': None}
    try:
        musicbrainz_search = [artist for artist in musicbrainzngs.search_artists(artist=artist)['artist-list']
                              if artist['ext:score'] == '100']
    except:
        print(fg(2) + 'some error with musicbrainz' + attr(0))
    else:
        artist_id = None
        if len(musicbrainz_search) > 1:
            [(print(str(i) + ': '),
              pprint(dict((k, musicbrainz_search[i][k]) for k in
                          ['name', 'alias-list', 'disambiguation', 'life-span', 'id'] if k in musicbrainz_search[i])))
             for i in range(0, len(musicbrainz_search))]
            artist_id = input(fg(6) + 'Enter id of artist you would like to choose: ' + attr(0))
        if musicbrainz_search:
            if artist_id:
                musicbrainz = artist_id
            else:
                musicbrainz = musicbrainz_search[0]['id']

            releases['musicbrainz'] = get_albums_from_musicbrainz(musicbrainz)

    try:
        discogs_search = discogs_cli.search(artist, type='artist')
    except:
        print(fg(2) + 'some error with discogs' + attr(0))
    else:
        # todo redo
        artist_id = None
        # if len(discogs_search) > 1:
        #     [pprint(i, ': ', discogs_search[i]) for i in range(0, len(discogs_search))]
        #     index = input('Enter id of artist you would like to choose:')
        if discogs_search:
            if artist_id:
                discogs = artist_id
            else:
                discogs = discogs_search[0].id

            releases['discogs'] = get_albums_from_discogs(discogs)
            # releases = requests.get('https://api.discogs.com/artists/' + discogs + '/releases'
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
    # pprint(releases)
    musicbrainz_id.append(musicbrainz)
    discogs_id.append(discogs)
    discography.append(releases)

    data = {'artist': artists,
            'musicbrainz_id': musicbrainz_id,
            'discogs_id': discogs_id,
            'discography': discography}  # discography can contain either musicbrainz or discogs ids
    dataframe = pandas.DataFrame.from_dict(data)
    dataframe.to_csv('library.csv', sep=',', encoding='utf-8')
