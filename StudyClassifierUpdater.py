import httplib2
import json
import os
import datetime
import subprocess
import sys
from os import listdir
from os.path import isfile, join


def get_all_wrongly_classified_windows(connection):
    connection.request('GET', '/parse/classes/WronglyClassifiedWindow', '', {
        "X-Parse-Application-Id": "thesis-app-id"
    })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    objects = results["results"]
    return objects


def get_individual_users(connection):
    connection.request('GET', '/parse/classes/WronglyClassifiedWindow', '', {
        "X-Parse-Application-Id": "thesis-app-id"
    })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    objects = results["results"]
    ids = [x["objectId"] for x in objects]
    return ids


def get_collective_users(connection):
    connection.request('GET', '/parse/classes/WronglyClassifiedWindow', '', {
        "X-Parse-Application-Id": "thesis-app-id"
    })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    objects = results["results"]
    ids = [x["objectId"] for x in objects]
    return ids


def get_classifier_configurations(connection):
    connection.request('GET', '/parse/classes/ClassifierConfiguration', '', {
        "X-Parse-Application-Id": "thesis-app-id"
    })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    objects = results["results"]
    ids = [x for x in objects]
    return ids


def get_classifier_link_from_id(connection, object_id):
    connection.request('GET', "/parse/classes/ClassifierTest/" + object_id, '', {
        "X-Parse-Application-Id": "thesis-app-id"
    })
    results = json.loads(connection.getresponse().read().decode("utf-8"))
    classifier = results["classifier"]
    url = classifier["url"]
    return url


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(f):
        os.makedirs(d)


def get_file_from_link(connection, link):
    connection.request('GET', link, '', {
        "X-Parse-Application-Id": "thesis-app-id"
    })
    return connection.getresponse().read()


def get_classifier_from_link(connection, link):
    connection.request('GET', link, '', {
        "X-Parse-Application-Id": "thesis-app-id"
    })
    return connection.getresponse().read()


def save_classifier_to_file(classifier, directory, filename):
    bytearrayforclassifer = bytearray(classifier)
    classifier_file = open(directory + filename, 'wb+')
    classifier_file.write(bytearrayforclassifer)
    classifier_file.close()


def extract_windows_for_individuals(connection, parseobjects, users):
    links_for_windows = [x["Window"]["url"] for x in parseobjects if users.__contains__(x["UserClassifierObjectID"])]
    windows = []
    for link in links_for_windows:
        windows.append(get_file_from_link(connection=connection, link=link))
    return windows


def save_windows_to_files(windows, directory):
    i = 0
    for window in windows:
        bytearrayforwindow = bytearray(window)
        window_file = open(directory + "window" + repr(i), 'wb+')
        window_file.write(bytearrayforwindow)
        window_file.close()
        i += 1


def get_classifiers(directory):
    files = [f for f in os.listdir(directory) if isfile(join(directory, f))]
    return [x for x in files if x.endswith(".model")]


def upload_file(connection, filename, fullfilename):
    connection.request('POST', '/parse/files/' + filename, open(fullfilename, 'rb').read(), {
        "X-Parse-Application-Id": "thesis-app-id",
        "Content-Type": "application/classifier"
    })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    url = results["url"]
    filename = url.rsplit('/', 1)[-1]
    return filename


def upload_classifiers(connection, object_id, filename_event, filename_sitstand):
    connection.request('PUT', '/parse/classes/ClassifierConfiguration/' + object_id, json.dumps({
        "EventClassifier": {
            "name": filename_event,
            "__type": "File"
        },
        "SitStandClassifier": {
            "name": filename_sitstand,
            "__type": "File"}
    }), {
                           "X-Parse-Application-Id": "thesis-app-id",
                           "Content-Type": "application/json"
                       })

    results = json.loads(connection.getresponse().read().decode("utf-8"))
    return results


def update_classifiers(connection, classifiers, classifier_configuration_object_ids, directory):
    filename0 = upload_file(connection=connection, filename=classifiers[0],
                            fullfilename=directory + "/" + classifiers[0])
    filename1 = upload_file(connection=connection, filename=classifiers[1],
                            fullfilename=directory + "/" + classifiers[1])

    for object_id in classifier_configuration_object_ids:
        if "sniffer" in classifiers[0]:
            upload_classifiers(connection, object_id, filename0, filename1)
        else:
            upload_classifiers(connection, object_id, filename1, filename0)
    return


# Establish a connection
datestring = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
print("started at " + datestring)

logfile = "log" + datestring + ".txt"
log = open(logfile, 'wb')

connection = httplib2.HTTPConnectionWithTimeout('46.101.208.96', 5050)
connection.connect()

# Get classifier configurations and wrongly classified windows
classifier_configurations = get_classifier_configurations(connection=connection)
wrongly_classified_windows = get_all_wrongly_classified_windows(connection=connection)

# Get userIDs for collective group
userids_for_collective_group = list(
        set([x["objectId"] for x in classifier_configurations if x["Group"] == "collective"]))

# Get windows for collective group
windows_for_collective_groups = extract_windows_for_individuals(connection, wrongly_classified_windows,
                                                                userids_for_collective_group)
if windows_for_collective_groups:

    # Next step is gonna take a while. Clone connection
    connection.close()
    # Save windows
    datestring = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    directory = "D:/Dropbox/Thesis/Data/" + "collective" + datestring + "/"
    # directory = "D:/Dropbox/Thesis/Data/collective2016-05-15-20-37-12"
    ensure_dir(directory)
    save_windows_to_files(windows_for_collective_groups, directory)


    # Run classifier create jar
    processArgs = ["java", "-jar", "D:\\Dropbox\\Thesis\\DataProcessing\\out\\artifacts\\StudyPipeline_jar\\DataProcessing.jar", directory, directory]
    wrappedProcess = subprocess.Popen(processArgs, stdout=log)
    wrappedProcess.wait()

    connection.connect()

    # For each classifier_configuration_object_id : update the classifiers
    classifiers = get_classifiers(directory)
    update_classifiers(connection=connection, classifiers=classifiers,
                       classifier_configuration_object_ids=userids_for_collective_group, directory=directory)

# Get userids of individuals in individual group
userids_for_individual_group = list(
        set([x["objectId"] for x in classifier_configurations if x["Group"] == "individual"]))

# Repeat the entire process for each of the individuals in the individual group
for userid in userids_for_individual_group:
    windows_for_user = extract_windows_for_individuals(connection=connection, parseobjects=wrongly_classified_windows,
                                                       users=[userid])

    if windows_for_user:
        datestring = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        directory = "D:/Dropbox/Thesis/Data/individual" + datestring + "/" + userid.replace(" ", "") + datestring + "/"

        connection.close()

        ensure_dir(directory)
        save_windows_to_files(windows_for_user, directory)

        processArgs = ["java", "-jar", "D:\\Dropbox\\Thesis\\DataProcessing\\out\\artifacts\StudyPipeline_jar\\DataProcessing.jar",
                       directory, directory]
        wrappedProcess = subprocess.Popen(processArgs, stdout=log)
        wrappedProcess.wait()

        connection.connect()

        classifiers = get_classifiers(directory)
        update_classifiers(connection=connection, classifiers=classifiers,
                           classifier_configuration_object_ids=[userid], directory=directory)

datestring = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
print("ended at " + datestring)

#usage python StudyClassifierUpdater.py
