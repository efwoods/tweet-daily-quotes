from flask import Flask, render_template
import requests, random
import base64
import hashlib
import os
import re
import json
import requests
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
from flask import Flask, request, redirect, session, url_for, render_template
from dotenv import dotenv_values
import random
import configparser
app = Flask(__name__)

config = dotenv_values('./config/.env')

# You will need to set a variable for your app to initialize it, as is typical at the start of every Flask app. You can also create a secret key for your app, so it’s a random string using the os package.
app = Flask(__name__)
app.secret_key = os.urandom(50)

# Back in your Python file, you can set up variables to get your environment variables for your client_id and client_secret. Additionally, you’ll need to define variables for the authorization URL as auth_url and the URL for obtaining your OAuth 2.0 token as token_url. You will also want to get the environment variable you set for your redirect URI and pass that into a new variable called redirect_uri.
client_id = config["CLIENT_ID"]
client_secret = config["CLIENT_SECRET"]
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
redirect_uri = config["REDIRECT_URI"]

# Now we can set the permissions you need for your bot by defining scopes. You can use the authentication mapping guide to determine what scopes you need based on your endpoints. 
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]

# Since Twitter’s implementation of OAuth 2.0 is PKCE-compliant, you will need to set a code verifier. This is a secure random string. This code verifier is also used to create the code challenge.
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

# In addition to a code verifier, you will also need to pass a code challenge. The code challenge is a base64 encoded string of the SHA256 hash of the code verifier.
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")


# To connect to manage Tweets endpoint, you’ll need an access token. To create this access token, you can create a function called make_token which will pass in the needed parameters and return a token.
def make_token():
    return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)

# Since your bot will Tweet random facts about cats, you will need to get these from somewhere. There is a cat fact API that you can call to get facts to Tweet. The function parse_fav_quote allows you to make a GET request to the cat fact endpoint and format the JSON response to get a fact you can later Tweet.
def parse_fav_quote():
    url = "https://efwoods.github.io/EvanWoodsFavoriteQuotes/quotesTwitterDB.json"
    fav_quote = requests.request("GET", url).json()
    quote = random.randint(0, len(fav_quote["quotes"]))
    return fav_quote["quotes"][quote]

# To Tweet the cat fact, you can make a function that will indicate it is Tweeting which helps debug and makes a POST request to the Manage Tweets endpoint.
def post_tweet(payload, token):
    print("Tweeting!")
    return requests.request(
        "POST",
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers={
            "Authorization": "Bearer {}".format(token["access_token"]),
            "Content-Type": "application/json",
        },
    )

'''def authenticate_tweepy():
    # read config
    api_key = config["API_KEY"]
    api_key_secret = config['API_KEY_SECRET']
    access_token = config['ACCESS_TOKEN']
    access_token_secret = config['ACCESS_TOKEN_SECRET']
    # authenticate
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api'''
    
def get_prior_tweets():
    url = "https://api.twitter.com/2/users/1537504318496047106/tweets?max_results=100"
    prev_quotes = requests.request("GET", url).json()
    return prev_quotes
   # search_url = "https://api.twitter.com/2/tweets/search/recent"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
#query_params = {'query': '#depressed','tweet.fields': 'author_id'}

@app.route("/parse")
def hello_world():
    return parse_fav_quote()
    # return render_template("index.html", title="Hello")

def parse_fav_quote():
    url = "https://efwoods.github.io/EvanWoodsFavoriteQuotes/quotesTwitterDB.json"
    fav_quote = requests.request("GET", url).json()
    quote = random.randint(0, len(fav_quote["quotes"]))
    return fav_quote["quotes"][quote]

# At this point, you’ll want to set up the landing page for your bot to authenticate. Your bot will log into a page that lists the permissions needed.
@app.route("/")
def demo():
    global twitter
    twitter = make_token()
    authorization_url, state = twitter.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)

# After you save the token, you can parse the cat fact using the function parse_fav_quote. You will also need to format the fav_quote  into a JSON object. After, you can pass the payload in as a payload into your post_tweet.
@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    token = twitter.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code,
    )
    st_token = '"{}"'.format(token)
    j_token = json.loads(st_token)
    r.set("token", j_token)
    
    fav_quote = parse_fav_quote()
    tweets = get_prior_tweets()
    while fav_quote in tweets:
        fav_quote = parse_fav_quote()
    payload = {"text": "{}".format(fav_quote)}
    response = post_tweet(payload, token).json()
    return response
