from featurizer import Featurizer
from utils import process_decisions, logger, load_pickle


class Run():

    def __init__(self, run, parameters):
        self.parameters = parameters
        self.featurizer = Featurizer(parameters)
        self.classifier = load_pickle(parameters["classifier_path"], parameters["classifier_name"])
        self.run_identifier = run
        self.decisions_history = []
        self.scores_history = []
        logger("Initializing run {} with parameters {}".format(self.run_identifier, parameters))

    def get_run(self):
        return self.run_identifier

    # pass all the history of the user writings!!!!
    # one decision per user
    # "nick":"subject4170",
    # "decision":1,
    # "score":3.1
    def get_decisions(self, user_writings, users):
        logger("Classifying writings for run {}".format(self.run_identifier))
        features = self.featurizer.get_features(user_writings) # should return features without user and in window
        decisions, scores = self.classifier.fit(features)
        self.decisions_history.append(decisions)
        self.scores_history.append(scores)
        formatted_decisions = process_decisions(users, self.decisions_history, self.scores_history)

        return formatted_decisions
