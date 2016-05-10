import httplib2
import json


def upload_file(connection, filename):
    connection.request('POST', '/parse/files/classifier2.model', open(filename, 'rb').read(), {
        "X-Parse-Application-Id": "app",
        "Content-Type": "application/classifier"
    })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    url = results["url"]
    filename = url.rsplit('/', 1)[-1]
    return filename


def get_classifier_object_ids(connection):
    connection.request('GET', '/parse/classes/ClassifierConfiguration', '', {
        "X-Parse-Application-Id": "app"
    })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    objects = results["results"]
    ids = [x["objectId"] for x in objects]
    return ids


def update_classifiers(connection, object_id, filename_event, filename_sitstand):
    connection.request('PUT', '/parse/classes/ClassifierConfiguration/' + object_id, json.dumps({
        "EventClassifier": {
            "name": filename_event,
            "__type": "File"
        },
        "SitStandClassifier": {
            "name": filename_sitstand,
            "__type": "File"}
    }), {
                           "X-Parse-Application-Id": "app",
                           "Content-Type": "application/json"
                       })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    return results


connection = httplib2.HTTPConnectionWithTimeout('localhost', 5001)
connection.connect()
filename_event = upload_file(connection=connection, filename="classifier2.model")
#print(filename_event)
filename_sitstand = upload_file(connection=connection, filename="classifier2.model")
#print(filename_sitstand)
ids = get_classifier_object_ids(connection=connection)
#print(ids)
for object_id in ids:
    print(update_classifiers(connection=connection, object_id=object_id, filename_event=filename_event,
                             filename_sitstand=filename_sitstand))
