from featurizer import Featurizer
from utils import process_decisions, logger, load_pickle, save_pickle


class Run():

    def __init__(self, run, params):
        self.params = params
        self.featurizer = Featurizer(params)
        self.classifier = load_pickle("pickles", params["classifier_name"])
        self.run_identifier = run
        self.decisions_history = []
        logger("Initializing run {} with parameters {}".format(self.run_identifier, params))

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
        decisions = self.classifier.predict(features)
        logger("There is positive decisions: {}".format(1 in decisions))
        if 1 in decisions:
            logger("Number of positive decisions: {}".format(len([decision for decision in decisions if decision==1])))
        scores = decisions
        formatted_decisions = process_decisions(users, decisions, scores)
        self.decisions_history.append(formatted_decisions)
        save_pickle("pickles", "decisions_history.pkl", self.decisions_history)
        return formatted_decisions

    def get_old_decisions(self):
        return self.decisions_history[-1]
