import http.client

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

def get_song_for(query):
    conn = http.client.HTTPConnection("www.mldb.org")
    url_query = query.replace(" ", "+").replace("'", "%27").replace(",", "%2C")
    conn.request('GET', '/search?mq={}&si=3&mm=0&ob=1'.format(url_query))
    resp = conn.getresponse()
    if resp.status == 200:
        html = resp.read().decode('utf-8')
        song_title_a = from_after_to_str(html, '<td class="ft">', "</td>")
        song_title = from_after_to_str(song_title_a, '>', '<')
        song_artist_a = from_after_to_str(html, '<td class="fa">', "</td>")
        song_artist = from_after_to_str(song_artist_a, '>', '<')
        return song_artist, song_title
    else:
        return None, None

