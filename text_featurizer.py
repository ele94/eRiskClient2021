# TODO
import string, re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.preprocessing import KBinsDiscretizer
import pandas as pd

class TextFeaturizer():

    def __init__(self, params):
        self.params = params
        self.est = KBinsDiscretizer() # TODO load trained discretizer
        self.nssi_corpus = load_nssi_corpus(params["nssi_corpus_path"])

    def featurize(self, window):

        if self.params["text_features"] == "all":
            feats = create_all_features(window, self.nssi_corpus, self.params["normalize"])
        else:
            feats = create_select_features(
                window, self.nssi_corpus, self.params["normalize"], prons=self.params["prons"], nssi=self.params["nssi"])

        if self.params["discretize"]:
            feats = self.discretize_features(feats)

        return feats

    def discretize_features(self, feats):
        discretized_feats = self.est.transform(feats)
        return discretized_feats


def create_select_features(window_df, nssi_corpus, normalize=True, prons=True, nssi=True):
    new_feats = pd.DataFrame()
    text_length = window_df['clean_text'].map(len)

    if prons:
        reg = r'\bI\b|\bme\b|\bmine\b|\bmy\b|\bmyself\b'
        new_feats['first_prons'] = window_df['clean_text'].map(lambda x: len(re.findall(reg, x)))

    if nssi:
        for key, values in nssi_corpus.items():
            new_feats[key] = window_df['stems'].map(lambda x: sum((' '.join(x)).count(word) for word in values))

    if normalize:
        for feature in new_feats.columns:
            new_feats[feature] = new_feats[feature] / text_length

    return new_feats


def create_all_features(window_df, nssi_corpus, normalize=True):
    normalize_exceptions = ['char_count', 'word_density']
    exclude_features = ['char_count', 'word_count']

    new_feats = pd.DataFrame()

    text_length = window_df['clean_text'].map(len)

    new_feats['char_count'] = window_df['clean_text'].map(len)
    new_feats['word_count'] = window_df['clean_text'].map(lambda x: len(x.split()))
    new_feats['word_density'] = text_length / (text_length + 1)

    new_feats['punctuation_count'] = window_df['clean_text'].map(
        lambda x: len("".join(_ for _ in x if _ in string.punctuation)))
    new_feats['upper_case_count'] = window_df['clean_text'].map(
        lambda x: len([wrd for wrd in x.split() if wrd.isupper()]))

    new_feats['questions_count'] = window_df['text'].map(lambda x: len(re.findall(r'\?', x)))
    new_feats['exclamations_count'] = window_df['text'].map(lambda x: len(re.findall(r'\!', x)))
    new_feats['smilies'] = window_df['text'].map(lambda x: len(re.findall(r'\:\)+|\(+\:', x)))
    new_feats['sad_faces'] = window_df['text'].map(lambda x: len(re.findall(r'\:\(+|\)+\:', x)))

    reg = r'\bI\b|\bme\b|\bmine\b|\bmy\b|\bmyself\b'
    new_feats['first_prons'] = window_df['clean_text'].map(lambda x: len(re.findall(reg, x)))

    sid = SentimentIntensityAnalyzer()
    new_feats['sentiment'] = window_df['clean_text'].map(lambda x: round(sid.polarity_scores(x)['compound'], 2))
    for key, values in nssi_corpus.items():
        new_feats[key] = window_df['stems'].map(lambda x: sum((' '.join(x)).count(word) for word in values))
    pos_family = {
        'noun': ['NN', 'NNS', 'NNP', 'NNPS'],
        'pron': ['PRP', 'PRP$', 'WP', 'WP$'],
        'verb': ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'],
        'adj': ['JJ', 'JJR', 'JJS'],
        'adv': ['RB', 'RBR', 'RBS', 'WRB']
    }

    def check_pos_tag(x, flag):
        test_list = [tag for (word, tag) in x if tag in pos_family[flag]]
        count = len(test_list)
        return count

    new_feats['noun_count'] = window_df['pos_tags'].map(lambda x: check_pos_tag(x, 'noun'))
    new_feats['pron_count'] = window_df['pos_tags'].map(lambda x: check_pos_tag(x, 'pron'))
    new_feats['verb_count'] = window_df['pos_tags'].map(lambda x: check_pos_tag(x, 'verb'))
    new_feats['adj_count'] = window_df['pos_tags'].map(lambda x: check_pos_tag(x, 'adj'))
    new_feats['adv_count'] = window_df['pos_tags'].map(lambda x: check_pos_tag(x, 'adv'))

    if normalize:
        for feature in new_feats.columns:
            if feature not in normalize_exceptions:
                new_feats[feature] = new_feats[feature] / text_length

    for feat in exclude_features:
        new_feats.drop(feat, inplace=True, axis=1)

    return new_feats



def load_nssi_corpus(nssi_corpus_path):

    with open(nssi_corpus_path, 'r') as file:
        nssi_corpus_original = file.read()

    nssi_corpus = nssi_corpus_original.replace('*', '')
    nssi_corpus = nssi_corpus.replace("Methods of NSSI", '')
    nssi_corpus = nssi_corpus.replace("NSSI Terms", '')
    nssi_corpus = nssi_corpus.replace("Instruments Used", '')
    nssi_corpus = nssi_corpus.replace("Reasons for NSSI", '')

    keys = ["methods", "terms", "instruments", "reasons"]

    nssi_corpus = nssi_corpus.split(':')
    nssi_corpus.remove('')
    nssi_corpus = [corpus.split("\n") for corpus in nssi_corpus]
    new_nssi_corpus = {}
    for idx, corpus in enumerate(nssi_corpus):
        new_list = [word for word in corpus if word != ""]
        new_nssi_corpus[keys[idx]] = new_list

    return new_nssi_corpus
