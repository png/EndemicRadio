from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
from .models import Artist, Song

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

SPOTIPY_CLIENT_ID="301991271dc74862a88cdc605316852b"
SPOTIPY_CLIENT_SECRET="68c5eae2f0754840985cc8793db15e5e"

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

def buildSongList(request):
    results = sp.search(q='weezer', limit=20)
    for idx, track in enumerate(results['tracks']['items']):
        print(idx, track['name'])

def getPlaylistByRegion(request, regionName):
    songList = [] # list of spotify ids
    artists = Artist.objects.filter(artistLocation=regionId)
    for artist in artists:
        songs = Song.objects.filter(artistId=artist.id)
        for song in songs:
            songList.append(song.spotifyId)
    resp = json.dumps(songList)
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
