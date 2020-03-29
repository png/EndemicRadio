from django.db import models

# Create your models here.

class Picture(models.Model):
    name = models.CharField(max_length=50)
    picture_image = models.ImageField(upload_to='images/')

class Artist(models.Model):
    artistName = models.CharField(max_length=100, unique=True)
    artistLocation = models.CharField(max_length=100)
    spotifyId = models.CharField(max_length=100, null=True, blank=True)
    profileImageLink = models.CharField(max_length=500, null=True,blank=True)
    searchedSpotify = models.BooleanField(default=False)

    @classmethod
    def create(cls, artistName, artistLocation):
        newArtist = cls(artistName=artistName, artistLocation=artistLocation)
        newArtist.save()
        return newArtist

    def integrateSpotify(self, spotifyId, profileImageLink):
        self.spotifyId = spotifyId
        self.profileImageLink = profileImageLink
        self.save()
        return self

    def searchedSpotifyDone(self):
        self.searchedSpotify = True
        self.save()
        return self


class Song(models.Model):
    songName = models.CharField(max_length=100)
    #spotifyId = models.CharField(max_length=100)
    songUrl = models.CharField(max_length=100)
    artistId = models.ForeignKey(Artist, on_delete=models.CASCADE)

    @classmethod
    def create(cls, name, songUrl, artistId):
        newSong = cls(songName=name, songUrl=songUrl, artistId=artistId)
        newSong.save()
        return newSong

class Location(models.Model):
    name = models.CharField(max_length=100)

    @classmethod
    def create(cls, name):
        newLocation = cls(name=name)
        newLocation.save()
        return newLocation
