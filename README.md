# pigeons-planes
A friend told me abut Complex's Pigeons and Planes, a music discovery platform. It's a great place to find new and rising artist. A list is published every month or so. Here's the basic layout of the list:

```
[Artist Name]
  [Artist summary]
  [Song from artist]
```

So here's where this script comes in. It will grab all of the Soundcloud and Youtube links from the HTML content, search for the song in Spotify and create a playlist.

## Getting Started
In order to run this script, you will need to install the dependencies below and create a Spotify application. The script requires a YAML config file, I included a template in the repo. 

### Dependencies
- Spotipy
- Yaml

### Setup
To run this project, run it in terminal
```
$ python pigeons_planes-scraper.py
```
