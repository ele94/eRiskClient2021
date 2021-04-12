from abc import abstractmethod
import requests, json, pickle, os
import xml.etree.ElementTree as ET

# TEST SERVER
get_request = "https://erisk.irlab.org/challenge-service/getwritings/{}"  # format: team token
post_request = "https://erisk.irlab.org/challenge-service/submit/{}/{}"  # format: team token, run number (0-4)

# ACTUAL SERVER
# get_request = "https://erisk.irlab.org/challenge-t2/getwritings/{}"
# post_request = "https://erisk.irlab.org/challenge-t2/submit/{}/{}"
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

