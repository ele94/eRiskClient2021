from sklearn.feature_extraction.text import TfidfVectorizer
from utils import load_pickle

class TfidfFeaturizer():

    def __init__(self, params):
        self.params = params
        self.tfidf_vect = TfidfVectorizer()
        self.tfidf_vect = load_pickle(params["pickles_path"], params["tfidf_vect_name"])

    def featurize(self, window):
        return self.tfidf_vect.transform(window["clean_text"])
