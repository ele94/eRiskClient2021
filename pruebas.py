from data_client import DataClient, ServerClient

client = ServerClient()

data = client.get_writings()
print(data)