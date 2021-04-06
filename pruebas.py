from data_client import DataClient, ServerClient

client = ServerClient()

data = client.get_writings()
print(data)



# load classifier(s) (different for different runs?)
# initialize user writings memory
    # if user writings memory pickle exists: load
    # else: create new

# initialize tfidf featurizer (load trained tfidf vect)

# start writings counter (?)

# create runs 1, 2, 3, 4, 5


# start loop:

    # while: condition (until no new messages, or until 100 messages, whatever) (maybe until no new messages but decision frozen at 100 messages for some)

    # get batch of writings

    # clean writings

    # save clean writins in user writings memory

    # save user writings memory to pickle

    # for n in n_runs:
        # get response to server for run n method for runs (parameters for runs)

        # assemble response to server

    # try catch:
        # send response to server


#(class runs)
# method for runs (parameters for runs):

    # use last x from user writings to get (parametrized) features for this iteration

    # use features to make prediction

    # use predictions to format response to server

    # return formatted response to server