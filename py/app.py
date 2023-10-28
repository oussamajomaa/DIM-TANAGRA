
# from transformers import pipeline
import csv
from function import analyze_sentence
import spacy
nlp = spacy.load('fr_core_news_sm')
# import spacy
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut
# import geonamescache

# Charger le modèle français de spaCy
# ! python -m spacy download fr_core_news_sm
# nlp = spacy.load('fr_core_news_sm')

# Charger la bdd geonames:
# gc = geonamescache.GeonamesCache()

# https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment
#sentiment_analysis_model = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", framework="tf")
# sentiment_analysis_model = pipeline(
#     "sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", framework="pt")



# blacklist = ["l’", "qu’", "m’", "t’", "s’", "L’"]

# with open("blacklist.txt", "r", encoding='utf-8') as file:
#  blacklist = [word.strip() for word in file.readlines()]


# def analyze_sentence(sentence):
#     geolocator = Nominatim(user_agent='my-app', timeout=10)
#     doc = nlp(sentence)
#     analyzed_sentence = []
#     entities = []
#     latitude = None
#     longitude = None
#     sentiment_score_sentence = 0
#     sentiment_label_sentence = ""

#     for ent in doc.ents:
#         if ent.label_ == "LOC":
#             if ent.text not in blacklist:
#                 entities.append(ent.text)

#                 # Geopy library will not be able to connect to the Nominatim server in order to geocode all locations, due to the connection timing out.
#                 # We can handle this issue in a few ways: Increase the timeout, Retry the request (try/except...) or use a DB like Geonames ou OpenStreetMap
#                 # pour le moment j'utilse un compteur à personnaliser "counter", voir plus loin.
#                 # Je vais utiliser geonamescache (geonames.db est plus complet mais plus lourd), et si l'info manque, j'appelle l'api geonames en ligne.

#                 # Try using Geonamescache as primary source
#                 matching_cities = gc.get_cities_by_name(ent.text)
#                 # essayer aussi: get_cities(), get_countries(), get_countries_by_names(), get_continents(), etc.
#                 if matching_cities:
#                     first_matching_city = list(matching_cities[0].values())[0]
#                     latitude = first_matching_city['latitude']
#                     longitude = first_matching_city['longitude']
#                 else:
#                     # Use Nominatim as fallback
#                     try:
#                         location = geolocator.geocode(ent.text)
#                         if location:
#                             latitude = location.latitude
#                             longitude = location.longitude
#                     except GeocoderTimedOut:
#                         location = None

#                 if entities and latitude and longitude:
#                     sentiment_score_sentence = sentiment_analysis_model(sentence)[
#                         0]["score"]
#                     sentiment_label_sentence = sentiment_analysis_model(sentence)[
#                         0]['label']
#                 result = {
#                     "entity": ent.text,
#                     "sentiment_label_sentence": sentiment_label_sentence,
#                     "sentiment_score_sentence": sentiment_score_sentence,
#                     "latitude": latitude,
#                     "longitude": longitude
#                 }
#                 analyzed_sentence.append(result)
#                 # print("analyzed sentences *** ", analyzed_sentence)

#     return analyzed_sentence

from flask import Flask, request, render_template, render_template_string

from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/text', methods=["POST"])
def getEntities():
    analyzed_sentences = []
    text = request.get_json(force=True)
    "Paris est belle. Paris est moche. Paris est grande. Paris est peuplée. Damas est belle."
    print(text)
    all_sentences = nlp(text)
    for sentence in all_sentences.sents:
        sentence = str(sentence)
        analyzed_sentence = analyze_sentence(sentence)
        for result in analyzed_sentence:
            entity = result["entity"]
            sentiment_label = result["sentiment_label_sentence"]
            sentiment_score = result["sentiment_score_sentence"]
            latitude = result["latitude"]
            longitude = result["longitude"]

            # check if latitude and longitude are None
            if latitude is None or longitude is None:
                # print(
                #     f"Skipping sentence due to missing location data: {sentence}")
                continue  # skip this sentence and move to the next one

            # writer.writerow(["-->", sentence, entity, sentiment_label,
            #                 round(sentiment_score, 2), latitude, longitude])
            # counter += 1
            # print(
            #     f"Sentiment de la phrase {counter}: {sentence[:20]}... ; entité:[{entity}] ; polarity: {sentiment_label} ; score: {round(sentiment_score, 2)}")
            analyzed_sentences.append({
                'sentence': sentence,
                'entity': entity,
                'sentiment_label': sentiment_label,
                'sentiment_score': round(sentiment_score, 2),
                'latitude': latitude,
                'longitude': longitude
            })

    # Iterate analyzed_sentences and create a new dictionary
    entities_dict = {}
    i = 1
    for sentence_info in analyzed_sentences:
        
        print("Length = ",len(entities_dict))
        entities_list = []
        entity = sentence_info['entity']
        sentiment_label = sentence_info['sentiment_label']

        # Initialize entity information if it doesn't exist
        if entity not in entities_dict:
            
            entities_dict[entity] = {
                'latitude': sentence_info['latitude'],
                'longitude': sentence_info['longitude'],
                'occurrences': 1,
                'positive_labels': 0,
                'negative_labels': 0,
                'neutral_labels': 0,
                'overall_sentiment': sentiment_label,
                'time':1500*i
            }
            i=i+1
            print(entities_dict[entity])
        else:
            print("Occurences ** ",entities_dict[entity]['occurrences'])
            entities_dict[entity]['occurrences'] +=1

        # Update sentiment label counts and overall sentiment
        if sentiment_label in ['4 stars', '5 stars']:
            entities_dict[entity]['positive_labels'] += 1
        elif sentiment_label in ['1 star', '2 stars']:
            entities_dict[entity]['negative_labels'] += 1
        elif sentiment_label == '3 stars':
            entities_dict[entity]['neutral_labels'] += 1

        # Update overall sentiment based on counts
        for entity in entities_dict:
            positive_count = entities_dict[entity]['positive_labels']
            negative_count = entities_dict[entity]['negative_labels']
            neutral_count = entities_dict[entity]['neutral_labels']

            if positive_count > negative_count and positive_count > neutral_count:
                entities_dict[entity]['overall_sentiment'] = 'Positive'
            elif negative_count > positive_count and negative_count > neutral_count:
                entities_dict[entity]['overall_sentiment'] = 'Negative'
            elif neutral_count > positive_count and neutral_count > negative_count:
                entities_dict[entity]['overall_sentiment'] = 'Neutral'
            else:
                entities_dict[entity]['overall_sentiment'] = 'Mixed'
            

            # entities_dict = list(entities_dict.values())
        entities_list = []
        entities_list = [{'name': key, **value} for key, value in entities_dict.items()]
        text = ""
        # entities_dict["entity"] = {}
    return entities_list

# print("entities_dict *** ", data_list)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=3333)

