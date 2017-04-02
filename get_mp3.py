import youtube_dl
import requests
#from os import remove
#import os.path

import sys
if sys.version_info[0] == 2:
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

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
        print("Youtube-dl::DEBUG", msg)
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

def get_video(url):
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
            "outtmpl": "downloads/curr_video",
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
    return from_after_to_str(html, '<p class="songtext" lang="EN">', "</p>").replace("<br />", "").replace("\n", " ")

def get_mp3_from_lyrics(lyrics):
    artist, title, link = get_song_for(lyrics)
    if artist is None:
        return "No song"
    print(artist, title)
#    url = get_url_by_song(artist, title)
#    if url is None:
#        return "No URL"
#    return get_video(url)
    print(quote_plus(' '.join([artist, title])))
    ret = get_video(quote_plus(' '.join([artist, title])))
    print(get_lyrics(link))
    return ret

print(get_mp3_from_lyrics("with love from me to you"))
