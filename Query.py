import httplib2
import json

connection = httplib2.HTTPConnectionWithTimeout('localhost', 5001)
connection.connect()
connection.request('GET', '/parse/classes/ClassifierTest', '', {
    "X-Parse-Application-Id": "app"
})

results = json.loads(connection.getresponse().read().decode("utf-8"))
print(results)

objects = results["results"]
print(objects)

ids = [x["objectId"] for x in objects]

print(ids)
