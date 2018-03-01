import discogs_client
import json
import errno
import lxml.html
import musicbrainzngs
import numpy
import os
import pandas
import platform
import pylast
import requests
import urllib.request
from colored import fg, attr
from datetime import datetime
from fabulous import utils, image
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from operator import itemgetter
from pprint import pprint
from tqdm import tqdm


def notify(artist, album, album_art, sound='Glass'):
    """Send os notification
        :param artist:
        :param album:
        :param sound:
    """
    print()
    print(fg(8) + "{} by {}".format(album, artist) + attr(0))

    # macOS notification
    # if platform.system() == 'Darwin':
    #     os.system("""
    #     osascript -e 'display notification "new album {} by {}" with title "new albums" sound name "{}"'
    #     """.format(album, artist, sound))
    os.system("""ntfy -b telegram send '{} by {}'""".format(album, artist))
    if album_art:
        os.system("""ntfy -b telegram send '{}'""".format(album_art))


# last.fm
api_key = 'your api key'
api_secret = 'your api secret'
username = 'your last.fm username'
password_hash = pylast.md5('')


def get_artists(plays=20):
    api = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret, username=username)
    artists = [artist.item.name for artist in pylast.User(username, api).get_library().get_artists(limit=None)
               if artist.playcount >= plays]

    return artists


# musicbrainz
musicbrainzngs.set_useragent("new-albums", "0.0.1", "https://github.com/nikitalpopov/new-albums")


def get_albums_from_musicbrainz(musicbrainz):
    albums = []
    # todo try to change release-group to official release
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


def get_data(artist):
    # print(fg(2) + artist + attr(0))
    tqdm.write(fg(2) + artist + attr(0))
    musicbrainz = None
    discogs = None
    musicbrainz_releases = None
    discogs_releases = None
    try:
        musicbrainz_search = [artist for artist in musicbrainzngs.search_artists(artist=artist)['artist-list']
                              if artist['ext:score'] == '100']
    except:
        # print(fg(2) + 'some error with musicbrainz' + attr(0))
        tqdm.write(fg(2) + 'some error with musicbrainz' + attr(0))
    else:
        artist_id = None
        if len(musicbrainz_search) > 1:
            artist_id = musicbrainz_search[0]['id']
            # [print('https://musicbrainz.org/artist/' + musicbrainz_search[i]['id'])
            #  if 'id' in musicbrainz_search[i] else None for i in range(0, len(musicbrainz_search))]
            # artist_id = input(fg(6) + 'Enter id of artist you would like to choose: ' + attr(0))
        if musicbrainz_search:
            if artist_id:
                musicbrainz = artist_id
            else:
                musicbrainz = musicbrainz_search[0]['id']

            musicbrainz_releases = get_albums_from_musicbrainz(musicbrainz)

    try:
        discogs_search = discogs_cli.search(artist, type='artist')
    except:
        # print(fg(2) + 'some error with discogs' + attr(0))
        tqdm.write(fg(2) + 'some error with discogs' + attr(0))
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

            discogs_releases = get_albums_from_discogs(discogs)
            # discogs_releases = requests.get('https://api.discogs.com/artists/' + discogs + '/releases'
            #                         + '?sort=year'
            #                         + '&sort_order=desc')
            # pprint(discogs_releases.json()['releases'])
            # print()
            # discogs_releases = requests.get('https://api.discogs.com/database/search'
            #                         + '?artist=' + artist
            #                         + '&year=' + str(datetime.now().year - 1)
            #                         + '&format=album'
            #                         + '&type=release'
            #                         + '&token=' + user_token)
            # pprint(discogs_releases.json()['results'])
            # print()
            # for release in discogs_search[0].releases:
            #     pprint(release)

    result = pandas.DataFrame(columns=['latest_update', 'musicbrainz_id', 'discogs_id', 'musicbrainz_discography',
                                       'discogs_discography', 'artist'])

    return result.append({'latest_update': datetime.today().date(), 'musicbrainz_id': musicbrainz,
                          'discogs_id': discogs, 'musicbrainz_discography': musicbrainz_releases,
                          'discogs_discography': discogs_releases, 'artist': artist}, ignore_index=True)


def get_new_releases(dataframe):
    musicbrainz_latest = dataframe[['artist', 'latest_update', 'musicbrainz_discography', 'musicbrainz_id']]
    discogs_latest = dataframe[['artist', 'latest_update', 'discogs_discography', 'discogs_id']]
    musicbrainz_latest['musicbrainz_discography'] = musicbrainz_latest['musicbrainz_discography']\
        .apply(lambda x: x[0] if x and len(x) > 0 and x[0]['date'] == datetime.today() else None)
    discogs_latest['discogs_discography'] = discogs_latest['discogs_discography']\
        .apply(lambda x: x[0] if x and len(x) > 0 and x[0]['date'] == datetime.today() else None)
    musicbrainz_latest = \
        musicbrainz_latest.replace(to_replace='None', value=numpy.nan).dropna()
    discogs_latest = discogs_latest.replace(to_replace='None', value=numpy.nan).dropna()

    writer = pandas.ExcelWriter("new_albums.xlsx")
    musicbrainz_latest.to_excel(writer, 'musicbrainz')
    discogs_latest.to_excel(writer, 'discogs')

    musicbrainz_latest = [(row['artist'],
                           row['musicbrainz_discography']['id'],
                           row['musicbrainz_discography']['title'],
                           row['musicbrainz_discography']['date']) for _, row in musicbrainz_latest.iterrows()]
    discogs_latest = [(row['artist'],
                       row['discogs_discography']['title'],
                       row['discogs_discography']['date']) for _, row in discogs_latest.iterrows()]

    # todo compare musicbrainz and discogs results and choose final list

    return musicbrainz_latest


# run script
artists = get_artists(50)

# get only new artists
# library_dump = pandas.read_csv('artists.csv', sep=',')
# artists = library_dump[~library_dump['artist'].isin(artists)].copy()
# artists = artists['artist'].tolist()

dataframe = pandas.DataFrame(columns=['artist', 'latest_update', 'musicbrainz_discography', 'musicbrainz_id',
                                      'discogs_discography', 'discogs_id'])

# with ThreadPool(cpu_count() - 1) as pool:
#     with tqdm(total=len(artists)) as pbar:
#         for i, _ in tqdm(enumerate(pool.starmap(get_data,
#                                             zip(range(0, len(artists)),
#                                                 [artists for _ in range(0, len(artists))],
#                                                 [dataframe for _ in range(0, len(artists))])))):
#             pbar.update()
#     # data = pool.map(get_data, tqdm(artists))
# pool.close()
# pool.join()

for artist in tqdm(artists):
    data = get_data(artist)
    dataframe = dataframe.append(data, ignore_index=True)
dataframe.to_csv('library.csv', sep=',', encoding='utf-8')
dataframe[['artist', 'musicbrainz_id', 'discogs_id', 'latest_update']].to_csv('artists.csv', sep=',', encoding='utf-8')

new_releases = get_new_releases(dataframe)
try:
    os.makedirs('./covers')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise
for (artist, album_id, album, date) in new_releases:
    try:
        urllib.request.urlretrieve('http://coverartarchive.org/release-group/' + album_id + '/front.jpg', './covers/' + album_id + '.jpg')
    except:
        album_art = None
    else:
        album_art = 'http://coverartarchive.org/release-group/' + album_id + '/front.jpg'

    notify(artist, album, album_art)

    if album_art:
        print(image.Image('./covers/' + album_id + '.jpg'))
    print(fg('yellow') + 'https://musicbrainz.org/release-group/' + album_id + '/' + attr(0))
    print(fg('yellow'), date.date(), attr(0))
