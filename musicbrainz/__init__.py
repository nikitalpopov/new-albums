import musicbrainzngs
from datetime import datetime
from operator import itemgetter


def get_albums(musicbrainz):
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
