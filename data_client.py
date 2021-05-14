from abc import abstractmethod
import requests, json, pickle, os
import xml.etree.ElementTree as ET
from utils import eval_performance

# TEST SERVER
# get_request = "https://erisk.irlab.org/challenge-service/getwritings/{}"  # format: team token
# post_request = "https://erisk.irlab.org/challenge-service/submit/{}/{}"  # format: team token, run number (0-4)

# ACTUAL SERVER
import utils

get_request = "https://erisk.irlab.org/challenge-t2/getwritings/{}"
post_request = "https://erisk.irlab.org/challenge-t2/submit/{}/{}"
team_token = "h2JqS59z9yifPxX1cUnrsNo0SJ+E57ZZneOg3kvd4A"


# class that obtains data from different sources into the format
# accepted by the program
class DataClient():

    def __init__(self):
        self.users = []

    # obtains one line of data at a time
    # simulates how the task works (if client is not serverclient)
    @abstractmethod
    def get_writings(self):
        pass

    # sends decisions (if server)
    @abstractmethod
    def send_decision(self, decisions, run=None):
        pass

    # reads all golden truth (if exists)
    @abstractmethod
    def get_g_truth(self):
        pass


# connects with task server and loads data
class ServerClient(DataClient):

    def __init__(self):
        super().__init__()

    # def get_all_writings(self):
    #     url_get = get_request.format(team_token)
    #     print(url_get)
    #
    #     r = requests.get(url=url_get)
    #     data = r.json()
    #
    #     self.users.extend([post['nick'] for post in data])
    #
    #     return self.users

    #TODO if error arises, return None
    def get_writings(self):
        url_get = get_request.format(team_token)
        print(url_get)
        r = requests.get(url=url_get)
        data = r.json()

        #self.users.extend([post['nick'] for post in data])

        return data

    # new change: only one run must be sent at a time with this method
    # be sure to send all runs before making another request
    def send_decision(self, decisions, run=None):

        if not run:
            run = 0

        url_post = post_request.format(team_token, run)
        r = requests.post(url=url_post, json=decisions)
        print("Post request for run {}: [{}]: {}".format(run, r.status_code, r.text))
        if r.status_code != 200:
            raise Exception("Server returned code {}".format(r.status_code))
        r.close()

        return r.status_code, r.text


class PickleClient(DataClient):

    def __init__(self, params):
        super().__init__()
        self.index = 0
        self.all_writings = self.get_all_writings(params)
        self.g_truth = self.get_g_truth()

    def get_g_truth(self):
        g_truth = {line.split()[0]: int(line.split()[1]) for line in open("data/t2_g_truth.txt")}
        return g_truth

    def get_all_writings(self, params):
        user_writings = utils.load_pickle(params["pickles_path"], params["clean_writings_name"])
        return user_writings

    def get_writings(self):

        users_slice = {}
        for user, writings_list in self.all_writings:
            if len(writings_list) >= self.index:
                users_slice[user] = writings_list[self.index]

        self.index += 1
        return users_slice

    def send_decision(self, decisions, run=None):

        if not run:
            run = 0

        results = eval_performance([decisions], self.g_truth)
        return results
