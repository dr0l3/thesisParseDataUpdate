import httplib2
import json
import os


def get_classifier_object_ids(connection):
    connection.request('GET', '/parse/classes/ClassifierTest', '', {
        "X-Parse-Application-Id": "app"
    })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    objects = results["results"]
    ids = [x["objectId"] for x in objects]
    return ids


def get_classifier_link_from_id(connection, object_id):
    connection.request('GET', "/parse/classes/ClassifierTest/" + object_id, '', {
        "X-Parse-Application-Id": "app"
    })
    results = json.loads(connection.getresponse().read().decode("utf-8"))
    classifier = results["classifier"]
    url = classifier["url"]
    return url


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(f):
        os.makedirs(d)


def get_classifier_from_link(connection,link):
    connection.request('GET', link, '', {
        "X-Parse-Application-Id": "app"
    })
    return connection.getresponse().read()

def save_classifier_to_file(classifier, directory,filename):
    bytearrayforclassifer = bytearray(classifier)
    classifier_file = open(directory+filename, 'wb+')
    classifier_file.write(bytearrayforclassifer)
    classifier_file.close()

connection = httplib2.HTTPConnectionWithTimeout('localhost', 5001)
connection.connect()

object_ids = get_classifier_object_ids(connection=connection)
classifier_links = []
for object_id in object_ids:
    classifier_links.append(get_classifier_link_from_id(connection=connection, object_id=object_id))

dir_file_name = "D:/Projekter/ParseDataUpdater/classifiers/"
ensure_dir(dir_file_name)
classifiers = []
for classifier_link in classifier_links:
    classifiers.append(get_classifier_from_link(connection=connection, link=classifier_link))

index = 1
for classifier in classifiers:
    filename = "classifier" + repr(index) + ".model"
    index += 1
    save_classifier_to_file(classifier, dir_file_name, filename)
