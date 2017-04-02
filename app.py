#memes memes memes memes
#this code was not stolen from the internet

from flask import Flask, request, send_from_directory
import os
import json
import requests
from get_mp3 import get_mp3_from_lyrics

try:
    port = int(os.environ.get('PORT', 5000))
except KeyError:
    port = 5000
app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.

with open("pat.txt", 'r') as f:
    tokens = f.readlines()
    PAT = tokens[0]
    #print PAT
    verify = tokens[1]
    #print verify


@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == verify:
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    path, errno = get_mp3_from_lyrics(message)
    if errno < -1:
        send_message(PAT, sender, path)
    else:
        send_attachment(PAT, sender, path)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def send_attachment(token, recipient, path):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"attachment": {"type": "audio",
          "payload": {
              "url": "https://blueberry-cake-16125.herokuapp.com/" + path
           }}}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

@app.route("/downloads/<path:path>")
def req_for_mp3(path):
    return send_from_directory("downloads", path)

if __name__ == '__main__':
    print port
    app.run(host='0.0.0.0', port=port)
