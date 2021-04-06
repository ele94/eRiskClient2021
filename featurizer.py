from utils import logger
from text_featurizer import TextFeaturizer
from tfidf_featurizer import TfidfFeaturizer
from scipy.sparse import hstack

class Featurizer():

    def __init__(self, params):

        self.params = params
        self.text_featurizer = TextFeaturizer(params)
        self.tfidf_featurizer = TfidfFeaturizer(params)

    # ALL writing per user!!! user - writings
    # returns features for only the LAST window
    def get_features(self, user_writings):

        logger("Windowfying data")
        window = windowfy(user_writings, self.params["feats_window_size"])  # obviamente, solo cogemos la ultima ventana de cada usuario!

        if self.params["feats"] == "combined":
            features_list = []
            logger("Creating text features")
            features_list.append(self.text_featurizer.featurize(window))
            logger("Creating tfidf features")
            features_list.append(self.tfidf_featurizer.featurize(window))
            logger("Combining features")
            features = combine_features(features_list)

        elif self.params["feats"] == "text":
            logger("Creating text features")
            features = self.text_featurizer.featurize(window)

        else:
            logger("Creating tfidf features")
            features = self.tfidf_featurizer.featurize(window)

        return features


def combine_features(features_list):
    combined_features = hstack(features_list)
    return combined_features


def windowfy(user_writings, window_size):

    window_users = {user: join_window_elements(writings[-window_size:]) for (user, writings) in user_writings.items()}
    return window_users


# joins the elements of a window of messages of one user
def join_window_elements(window: list) -> dict:
    joint_window = {}
    flatten = lambda l: [item for sublist in l for item in sublist]

    for key in window[0].keys():
        key_list = [message[key] for message in window]
        if type(key_list[0]) is list:
            joint_window[key] = flatten(key_list)
        elif key == 'user':
            joint_window[key] = key_list[0]
        elif key == 'date':
            joint_window[key] = key_list
        elif key == 'round':
            joint_window[key] = key_list[-1]
        else:
            joint_window[key] = ' .'.join(key_list)

    return joint_window
