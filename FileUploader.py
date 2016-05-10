import httplib2
import json

connection = httplib2.HTTPConnectionWithTimeout('localhost', 5001)
connection.connect()
connection.request('POST', '/parse/files/classifier2.model', open('classifier2.model', 'rb').read(), {
    "X-Parse-Application-Id": "app",
    "Content-Type": "application/classifier"
})
temp = connection.getresponse().read().decode("utf-8")
print(temp)
results = json.loads(temp)
url = results["url"]
print(results)
print(url)
