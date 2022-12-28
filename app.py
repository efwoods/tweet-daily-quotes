from flask import Flask, render_template
import requests, random

app = Flask(__name__)

@app.route("/")
def hello_world():
    return parse_fav_quote()
    # return render_template("index.html", title="Hello")

def parse_fav_quote():
    url = "https://efwoods.github.io/EvanWoodsFavoriteQuotes/quotesTwitterDB.json"
    fav_quote = requests.request("GET", url).json()
    quote = random.randint(0, len(fav_quote["quotes"]))
    return fav_quote["quotes"][quote]
