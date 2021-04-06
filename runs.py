from featurizer import Featurizer
from utils import process_decisions, logger


class Run():

    def __init__(self, run, parameters, classifier):
        self.parameters = parameters
        self.featurizer = Featurizer(parameters)
        self.classifier = classifier
        self.run_identifier = run
        logger("Initializing run {} with parameters {}".format(self.run_identifier, parameters))


    # pass all the history of the user writings
    # one decision per user
    # "nick":"subject4170",
    # "decision":1,
    # "score":3.1
    def get_decisions(self, user_writings, users):
        logger("Classifying writings for run {}".format(self.run_identifier))
        features = self.featurizer.get_features(user_writings) # should return user - features
        decisions, scores = self.classifier.fit(features)
        formatted_decisions = process_decisions(users, decisions, scores)

        return formatted_decisions