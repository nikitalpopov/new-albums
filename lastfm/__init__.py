import pylast


def get_artists(api_key, api_secret, username, plays=20):
    api = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret, username=username)
    artists = [artist.item.name for artist in pylast.User(username, api).get_library().get_artists(limit=None)
               if artist.playcount >= plays]

    return artists
