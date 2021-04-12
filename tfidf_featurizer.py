from sklearn.feature_extraction.text import TfidfVectorizer
from utils import load_pickle, logger

class TfidfFeaturizer():

    def __init__(self, params):
        self.params = params
        self.tfidf_vect = TfidfVectorizer()
        self.tfidf_vect = load_pickle("pickles", params["tfidf_vect_name"])

    def featurize(self, window):
        tfidf_feats = self.tfidf_vect.transform(window["clean_text"])
        return tfidf_feats
