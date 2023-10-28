
import pandas as pd
import json

from flask import Flask, request
from flask_cors import CORS
import spacy
from textblob import TextBlob
import mysql.connector
from itertools import groupby
from operator import itemgetter
import folium
from deep_translator import GoogleTranslator

# nlp = en_core_web_md.load()
# nlp = spacy.load('en_core_web_sm')
nlp = spacy.load('fr_core_news_sm')
label = "LOC"

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def getCoord():
    # Connect to the database
    cnx = mysql.connector.connect(
        user='osm', password='osm', host='127.0.0.1', database='location')

    # Create a cursor
    cursor = cnx.cursor()

    # Execute a SQL statement
    cursor.execute("SELECT * FROM cities")
    # Fetch the results
    # results = dict(zip(cursor.column_names, cursor.fetchall()))
    columns = cursor.description
    results = [{columns[index][0]:column for index,
                column in enumerate(value)} for value in cursor.fetchall()]

    return results


# @app.route("/")
# def fullscreen():
#     """Simple example of a fullscreen map."""
#     # m = folium.Map()
#     return render_template('index.html')




@app.route('/text', methods=["POST"])
def getEnt():
    map = folium.Map(location=[20, 0], tiles="OpenStreetMap", zoom_start=2)
    body = request.get_json(force=True)
    res_coord = []
    try:
        # Get body request

        nlp = spacy.load('en_core_web_sm')
        label = "GPE"

        tokens = nlp(body)

        entities = []
        sentences = []

        # split tokens into sentences
        for sentence in tokens.sents:
            sentence = str(sentence)
            sentence = GoogleTranslator(source="auto", target="en").translate(sentence) 
            ents = nlp(str(sentence)).ents

            # Create a TextBlob object
            blob = TextBlob(sentence)
            sentiment = blob.sentiment.polarity
            sentences.append(sentence)
            for ent in ents:
                if ent.label_ == label:
                    if sentiment > 0:
                        entities.append(
                            {"name": ent.text, "emotion": "Positive"})
                    elif sentiment < 0:
                        entities.append(
                            {"name": ent.text, "emotion": "Negative"})
                    else:
                        entities.append(
                            {"name": ent.text, "emotion": "Neutral"})

        print('entities **** ', entities)
        results = []

        # Sort entities data by "place" key.
        entities = sorted(entities, key=itemgetter('name'))

        # Group entities data by "place" key
        for key, value in groupby(entities, key=itemgetter('name')):
            emotion = []
            i=0
            for k in value:
                i=i+1
                emotion.append(k["emotion"])

            results.append({"name": key, "country": "",
                           "overall_sentiment": emotion, "latitude": 0, "longitude": 0, "occurrences":i})

        # Compare the number of emotion for every "place" and save the big number

            for res in results:
                pos = res['overall_sentiment'].count('Positive')
                neg = res['overall_sentiment'].count('Negative')
                if pos > neg:
                    res['overall_sentiment'] = "Positive"
                elif pos < neg:
                    res['overall_sentiment'] = "Negative"
                else:
                    res['overall_sentiment'] = "Neutral"

        
        cities = getCoord()
        for loc in results:
            for city in cities:
                if city["name"] == loc["name"]:
                    item = {
                        'name': loc["name"],
                        'country': city["country"],
                        'overall_sentiment': loc["overall_sentiment"],
                        'latitude': city["lat"],
                        'longitude': city["lng"],
                        'id': city["id"],
                        'occurrences': loc["occurrences"]
                    }
                    res_coord.append(item)
                    # break

            
    except:
        print("Error")

    print(res_coord)
    return res_coord


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=3333)


