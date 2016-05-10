import httplib2
import json

connection = httplib2.HTTPSConnectionWithTimeout('google.com', 80)
connection.connect()
connection.request('POST', '/1/classes/Classifiers', json.dumps({
    "type" : "sniffer",
    "classifer": {
        "name": "classifier2.model",
        "__type": "File"
    }
}, {"X-Parse-Application-Id": "app",
    "X-Parse-REST-API-Key": "master",
    "Content-Type": "application/json"}
))
result = json.loads(connection.getresponse().read())
print(result)
