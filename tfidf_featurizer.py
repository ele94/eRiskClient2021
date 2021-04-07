# TODO
from sklearn.feature_extraction.text import TfidfVectorizer

class TfidfFeaturizer():

    def __init__(self, params):
        self.params = params
        self.tfidf_vect = TfidfVectorizer()
        # TODO load trained tfidf vector

    def featurize(self, window):
        return self.tfidf_vect.transform(window["clean_text"])
