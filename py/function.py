
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import spacy
nlp = spacy.load('fr_core_news_sm')
import geonamescache
blacklist = ["l’", "qu’", "m’", "t’", "s’", "L’"]
gc = geonamescache.GeonamesCache()
from transformers import pipeline
sentiment_analysis_model = pipeline(
    "sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", framework="pt")

def analyze_sentence(sentence):
    geolocator = Nominatim(user_agent='my-app', timeout=10)
    doc = nlp(sentence)
    analyzed_sentence = []
    entities = []
    latitude = None
    longitude = None
    sentiment_score_sentence = 0
    sentiment_label_sentence = ""

    for ent in doc.ents:
        if ent.label_ == "LOC":
            if ent.text not in blacklist:
                entities.append(ent.text)

                # Geopy library will not be able to connect to the Nominatim server in order to geocode all locations, due to the connection timing out.
                # We can handle this issue in a few ways: Increase the timeout, Retry the request (try/except...) or use a DB like Geonames ou OpenStreetMap
                # pour le moment j'utilse un compteur à personnaliser "counter", voir plus loin.
                # Je vais utiliser geonamescache (geonames.db est plus complet mais plus lourd), et si l'info manque, j'appelle l'api geonames en ligne.

                # Try using Geonamescache as primary source
                matching_cities = gc.get_cities_by_name(ent.text)
                # essayer aussi: get_cities(), get_countries(), get_countries_by_names(), get_continents(), etc.
                if matching_cities:
                    first_matching_city = list(matching_cities[0].values())[0]
                    latitude = first_matching_city['latitude']
                    longitude = first_matching_city['longitude']
                else:
                    # Use Nominatim as fallback
                    try:
                        location = geolocator.geocode(ent.text)
                        if location:
                            latitude = location.latitude
                            longitude = location.longitude
                    except GeocoderTimedOut:
                        location = None

                if entities and latitude and longitude:
                    sentiment_score_sentence = sentiment_analysis_model(sentence)[
                        0]["score"]
                    sentiment_label_sentence = sentiment_analysis_model(sentence)[
                        0]['label']
                result = {
                    "entity": ent.text,
                    "sentiment_label_sentence": sentiment_label_sentence,
                    "sentiment_score_sentence": sentiment_score_sentence,
                    "latitude": latitude,
                    "longitude": longitude
                }
                analyzed_sentence.append(result)
                # print("analyzed sentences *** ", analyzed_sentence)

    return analyzed_sentence