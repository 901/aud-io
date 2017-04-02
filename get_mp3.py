import youtube_dl
import requests
from pydub import AudioSegment
#from os import remove
#import os.path

import sys
if sys.version_info[0] == 2:
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

ctr = 0
def provide_counter(fn):
    def f(*args):
        global ctr
        ctr = ctr + 1
        return fn(*(args + (ctr - 1,)))
    return f

def from_after_to_str(string, from_k, to_k, start=0):
    lep = string.find(from_k, start)
    if lep < 0:
        return ""
    lep += len(from_k)
    rep = string.find(to_k, lep)
    if rep < 0:
        return string[lep:]
    else:
        return string[lep: rep]

def query_url(base_url, query_params):
    r = requests.get(base_url, params=query_params)
    return r

def get_song_for(query):
    resp = query_url("http://www.mldb.org/search", {'mq': query, 'si': 3, 'mm': 0, 'ob': 1})
    if resp.status_code == 200:
#        html = resp.raw.read().decode('utf-8')
        html = resp.text#.encode('ascii')
        song_title_a = from_after_to_str(html, '<td class="ft">', "</td>")
        song_title = from_after_to_str(song_title_a, '>', '<')
        song_link = from_after_to_str(song_title_a, 'href="', '"')
        song_artist_a = from_after_to_str(html, '<td class="fa">', "</td>")
        song_artist = from_after_to_str(song_artist_a, '>', '<')
        return song_artist, song_title, "http://www.mldb.org/" + song_link
    else:
        return None, None, None

class GetFileNameLogger():
    def __init__(self):
        self.file = ""
    def debug(self, msg):
        wds = msg.split(' ')
        if wds[0] == "[ffmpeg]" and wds[1] == "Destination:":
            self.file = wds[2]
            print("File downloaded")
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

@provide_counter
def get_video(url, ct):
    gfnl = GetFileNameLogger()
    ydl_opts = {
            "keepvideo": False,
            "include_ads": False,
            "noplaylist": True,
            "no_warnings": True,
            "postprocessors":[{
                    'key':'FFmpegExtractAudio',
                    'preferredcodec':'mp3',
                    'preferredquality':'192'
                }],
            "outtmpl": "downloads/video_" + str(ct),
            "allsubtitles": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "forcefilename": True,
            "logger": gfnl,
            "default_search": "http://www.youtube.com/results?q=",
            "max_downloads": 1
    }

#    if os.path.exists('downloads/curr_video.mp3'):
#        os.remove('downloads/curr_video.mp3')
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except:
            pass
    return gfnl.file

#def get_url_by_song(artist, title):
#    resp = query_url("http://www.youtube.com/results", {'q': ' '.join([artist, title])})
#    while resp.status_code in [301, 307]:
#        resp = query_url("www.youtube.com/results", {'q': ' '.join([artist, title])})
#    if resp.status_code == 200:
#        html = resp.raw.read().decode('utf-8')
#        first_result_h3 = from_after_to_str(html, '<h3 class="yt-lookup-title">', '</h3>')
#        first_result_url = from_after_to_str(first_result_h3, 'href="', '"')
#        return first_result_url
#    print("RIP, youtube:", resp.status)

def get_lyrics(link):
    html = requests.get(link).text
    return from_after_to_str(html, '<p class="songtext" lang="EN">', "</p>").replace("<br />", "").replace("\n", "")

def truncate_mp3(file, lyrics, query):
    INTRO_FUDGE = 5*1000
    END_FUDGE = 1000
    MIN_INTERVAL = 5000
    idx = -1
    match_len = 0
    for i in range(len(query), 1, -1):
        idx = lyrics.find(query[:i])
        if idx >= 0:
            match_len = i
            break
    if idx < 0:
        return False
    else:
        audio = AudioSegment.from_mp3(file)
        start_ms = len(audio) * idx / len(lyrics) + INTRO_FUDGE
        duration = max(MIN_INTERVAL, len(audio) * match_len / len(lyrics) + END_FUDGE)
        end_ms = start_ms + duration
        print("Guessed interval:", start_ms, end_ms)
        with open(file, 'wb') as out:
            audio[start_ms:end_ms].export(out, format='mp3')
        return True

def get_mp3_from_lyrics(lyrics):
    artist, title, link = get_song_for(lyrics)
    if artist is None:
        return "No song", -2
    print(artist, title)
#    url = get_url_by_song(artist, title)
#    if url is None:
#        return "No URL"
#    return get_video(url)
    print(quote_plus(' '.join([artist, title])))
    ret = get_video(quote_plus(' '.join([artist, title])))
    if ret is None:
        return "Could not find video", -2
    if not truncate_mp3(ret, get_lyrics(link).lower(), lyrics.lower()):
        return ret, -1
    return ret, 0

print(get_mp3_from_lyrics("don't stop me now I'm having a good time"))
