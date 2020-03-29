from django.shortcuts import render

from django.http import JsonResponse
from django.template import loader
import json
import requests
from .models import Artist, Song

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

SPOTIPY_CLIENT_ID="ae3080ed7da64ddeb73aac2b7be0b86c"
SPOTIPY_CLIENT_SECRET="3bfc3c5c449046d09dca01182c66e589"

def login(request):
    return render(request, 'stream/login.html', {})


def musicpage(request):
    return render(request, 'stream/musicpage.html', {})


def logout(request):
    return render(request, 'stream/logout.html', {})

def player(request):
    return render(request, 'stream/player.html', {})

def wikipediaUpdate(request):
    introText = "Category:Musical groups from "
    lengthIntro = len(introText)

    query = "https://en.wikipedia.org/w/api.php?cmdir=desc&format=json&list=categorymembers&action=query&cmlimit=500&cmtitle="
    response = requests.get(query+"Category:Musical_groups_by_city_in_the_United_States")
    if response.status_code == 200:
        content = json.loads(response.text)
        categories = content["query"]["categorymembers"]
        for category in categories:
            print(category["title"][lengthIntro:])
            regionQueryName = category["title"].replace(" ", "_")
            regionResponse = requests.get(query+regionQueryName)
            regionContent = json.loads(regionResponse.text)
            artists = regionContent["query"]["categorymembers"]
            for artist in artists:
                if artist["ns"] != 0: # additional subgroup
                    continue
                Artist.objects.filter(artistName=artist["title"]).delete() # remove redundancies
                curArtist = Artist.create(artist["title"], category["title"][lengthIntro:])
    return render(request, 'wikipedia.html')


# https://developer.spotify.com/console/get-search-item/?q=Muse&type=track%2Cartist&market=US&limit=10&offset=5
def getSongFromArtist(artist):
    token = util.prompt_for_user_token("zac",
                           "streaming",
                           client_id=SPOTIPY_CLIENT_ID,
                           client_secret=SPOTIPY_CLIENT_SECRET,
                           redirect_uri='http://endemicradio.herokuapp.com/')
    spotify = spotipy.Spotify(auth=token)
    sp = spotify
    if (artist.spotifyId == None): # get spotify Id if not received yet
        results = sp.search(q=artist.artistName.replace(" ", "+"), limit=20, type='artist') # encode spaces with '+'s
        # print(results)
        # try:
        print(artist.artistName)
        try:
            curArtist = results["artists"]["items"][0] # get the first entry that comes from the search
            artist.integrateSpotify(curArtist["uri"], curArtist["images"][0]["url"])
        except:
            return
        # except:
            # return

    # populate song information in DB
    trackResults = spotify.artist_top_tracks(artist.spotifyId)
    # print("tracks")
    # print(trackResults)
    for track in trackResults['tracks'][:10]:
        Song.create(track["name"], track["uri"], artist)

#
# playlist/<slug:regionName>'
#
def getPlaylistByRegion(request, regionName):
    regionName = regionName.replace("_"," ").replace("-", ",")
    songList = [] # list of spotify ids
    artists = Artist.objects.filter(artistLocation=regionName)
    for artist in artists:
        songs = Song.objects.filter(artistId=artist.id)
        if len(songs) == 0:
            getSongFromArtist(artist) # get from spotify and populate datatbase on requets for artist
        for song in songs:
            songList.append(song.spotifyId)
    # resp = json.dumps(songList)
    resp = {"songs":songList}
    return JsonResponse(resp)



# # stream video: https://stackoverflow.com/questions/33208849/python-django-streaming-video-mp4-file-using-httpresponse
# # for video streaming
# range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

# # streaming video
# class RangeFileWrapper(object):
#     def __init__(self, filelike, blksize=8192, offset=0, length=None):
#         self.filelike = filelike
#         self.filelike.seek(offset, os.SEEK_SET)
#         self.remaining = length
#         self.blksize = blksize

#     def close(self):
#         if hasattr(self.filelike, 'close'):
#             self.filelike.close()

#     def __iter__(self):
#         return self

#     def __next__(self):
#         if self.remaining is None:
#             # If remaining is None, we're reading the entire file.
#             data = self.filelike.read(self.blksize)
#             if data:
#                 return data
#             raise StopIteration()
#         else:
#             if self.remaining <= 0:
#                 raise StopIteration()
#             data = self.filelike.read(min(self.remaining, self.blksize))
#             if not data:
#                 raise StopIteration()
#             self.remaining -= len(data)
#             return data

# """
# When requesting a video, the video is sent in packets so that the user may consume the video more smoothly
# """
# def stream_video(request, path):
#     range_header = request.META.get('HTTP_RANGE', '').strip()
#     range_match = range_re.match(range_header)
#     size = os.path.getsize(path)
#     content_type, encoding = mimetypes.guess_type(path)
#     content_type = content_type or 'application/octet-stream'
#     if range_match:
#         first_byte, last_byte = range_match.groups()
#         first_byte = int(first_byte) if first_byte else 0
#         last_byte = int(last_byte) if last_byte else size - 1
#         if last_byte >= size:
#             last_byte = size - 1
#         length = last_byte - first_byte + 1
#         resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length), status=206, content_type=content_type)
#         resp['Content-Length'] = str(length)
#         resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
#     else:
#         resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
#         resp['Content-Length'] = str(size)
#     resp['Accept-Ranges'] = 'bytes'
#     return resp
# # Create your views here.
