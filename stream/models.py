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


class Song(models.Model):
    songName = models.CharField(max_length=100)
    spotifyId = models.CharField(max_length=100)
    artistId = models.ForeignKey(Artist, on_delete=models.CASCADE)

    @classmethod
    def create(cls, name, spotifyId, artistId):
        newSong = cls(songName=name, spotifyId=spotifyId, artistId=artistId)
        newSong.save()
        return newSong

