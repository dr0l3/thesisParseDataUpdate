import httplib2
import json

connection = httplib2.HTTPConnectionWithTimeout('localhost', 5001)
connection.connect()
connection.request('POST', '/parse/classes/TestObject', json.dumps(
        {
            "type": "sniffer",
            "stuff": "blah"
        }), {
                       "X-Parse-Application-Id": "app",
                       "X-Parse-REST-API-Key": "blah",
                       "Content-Type": "application/json"
                   })
results = connection.getresponse().read()
print(results)
