
from django.shortcuts import render, redirect
from django.template import loader
from .forms import *
from django.http import HttpResponse



from django.http import JsonResponse

import json
import requests
import random
from .models import Artist, Song, Location


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

SPOTIPY_CLIENT_ID="ae3080ed7da64ddeb73aac2b7be0b86c"
SPOTIPY_CLIENT_SECRET="3bfc3c5c449046d09dca01182c66e589"


def login(request):
    return render(request, 'stream/login.html', {})


def product(request):
    return render(request, 'stream/product.html', {})


def about(request):
    return render(request, 'stream/about.html', {})


def musicpage(request):
    if request.method == 'POST':
        form = PictureForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            #return render(request, 'stream/logout.html', {})

    else:
        form = PictureForm()

    return render(request, 'stream/musicpage.html', {'form': form})


def success(request):
    return HttpResponse('successfully uploaded')


def logout(request):
    return render(request, 'stream/logout.html', {})

def player(request, location):
    #generate player
    songList = getPlaylistByRegionFunc(location)
    locationUrl = location.replace("_"," ").replace("-", ",")
    imageList = None
    return render(request, 'stream/player.html', {"songs":songList, "images":imageList, "location":location, "locationUrl":locationUrl, "startUrl":songList['songs'][0]['url'], "startString":songList['songs'][0]['artist']+" - "+songList['songs'][0]['title']})

def locationSelect(request):
    #determine user location
    if request.method == "POST":
        pass
    else:
        locations = Location.objects.all()
    return render(request, 'stream/selectlocation.html', {'locations':locations})

def getArtistsByRegion(request, region):
    print(region)
    regionName = region.replace("_"," ").replace("-", ",")
    artists = Artist.objects.filter(artistLocation=regionName)
    artistList = {'names':[]}
    for artist in artists:
        artistList['names'].append(artist.artistName)
    print(artistList)
    return JsonResponse(artistList)

def wikipediaUpdate(request):

    query = "https://en.wikipedia.org/w/api.php?cmdir=desc&format=json&list=categorymembers&action=query&cmlimit=500&cmtitle="
    searches = [["Category:Musical_groups_by_city_in_the_United_States", "Category:Musical groups from "], ["Category:American_musicians_by_city", "Category:Musicians_from_"]]
    for search in searches:
        response = requests.get(query+search[0])
        introText = search[1]
        lengthIntro = len(introText)
        if response.status_code == 200:
            content = json.loads(response.text)
            categories = content["query"]["categorymembers"]
            for category in categories:
                if "Virginia" in category["title"] or "D.C." in category["title"]:
                    location = category["title"][lengthIntro:]
                    if("D.C." in location):
                        print("Found DC")
                        location = "Washington, DC"
                    Location.create(location)
                    regionQueryName = category["title"].replace(" ", "_")
                    regionResponse = requests.get(query+regionQueryName)
                    regionContent = json.loads(regionResponse.text)
                    artists = regionContent["query"]["categorymembers"]
                    for artist in artists:
                        if artist["ns"] != 0: # additional subgroup
                            continue
                        print(artist["title"])
                        Artist.objects.filter(artistName=artist["title"]).delete() # remove redundancies
                        curArtist = Artist.create(artist["title"], category["title"][lengthIntro:])

    return render(request, 'wikipedia.html')


# https://developer.spotify.com/console/get-search-item/?q=Muse&type=track%2Cartist&market=US&limit=10&offset=5
availableSongs=["bensound-summer.mp3", "bensound-tomorrow.mp3", "bensound-creativeminds.mp3", "bensound-ukulele.mp3"]
def getSongFromArtist(artist):

    token = util.prompt_for_user_token("zac",
                           "streaming",
                           client_id=SPOTIPY_CLIENT_ID,
                           client_secret=SPOTIPY_CLIENT_SECRET,
                           redirect_uri='http://endemicradio.herokuapp.com/')
    spotify = spotipy.Spotify(auth=token)
    sp = spotify

    if (artist.spotifyId == None and not artist.searchedSpotify): # get spotify Id if not received yet
        results = sp.search(q=artist.artistName.replace(" ", "+"), limit=20, type='artist') # encode spaces with '+'s
        # print(results)
        # try:
        print("Searching for", artist.artistName)
        try:
            curArtist = results["artists"]["items"][0] # get the first entry that comes from the search
            artist.integrateSpotify(curArtist["uri"], curArtist["images"][0]["url"])
            artist.searchedSpotifyDone()
        except:
            print("No Spotify Results for", artist.artistName)
            artist.searchedSpotifyDone()
            return

        trackResults = spotify.artist_top_tracks(artist.spotifyId)

        # print("tracks")
        # print(trackResults)
        for track in trackResults['tracks'][:10]:
            print(track["name"])
            Song.create(track["name"], random.choice(availableSongs), artist)
            #Song.create(track["name"], track["uri"], artist)
            # return


    # populate song information in DB


#
# playlist/<slug:regionName>'
#
def getPlaylistByRegion(request, regionName):
    return JsonResponse(getPlaylistByRegionFunc(regionName))


def getPlaylistByRegionFunc(regionName):
    regionName = regionName.replace("_"," ").replace("-", ",")
    songList = [] # list of spotify ids
    artists = Artist.objects.filter(artistLocation=regionName)
    for artist in artists:
        songs = Song.objects.filter(artistId=artist.id)
        if len(songs) == 0:
            getSongFromArtist(artist) # get from spotify and populate datatbase on requets for artist
        for song in songs:
            songList.append({
                "url" : song.songUrl,
                "title" : song.songName,
                "artist" : artist.artistName,
                })
    # resp = json.dumps(songList)
    random.shuffle(songList)
    resp = {"songs":(songList)}
    return resp




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
