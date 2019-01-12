from flask import Flask, render_template, request
from pymongo import MongoClient
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cnf1miou0vdt9d1qe8sx164zejp3fnay'
mongoClient = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
pubSubDb = mongoClient.appdb
publishedDataDb = pubSubDb.pubData

topics = ['Football', 'Movies', 'TV Shows', 'Gadgets', 'World News']
publishedData = dict()
subscribedUser = dict()
subscribedData = dict()
username = list()
notifyUsers = {'Football': False, 'Movies': False, 'TV Shows': False, 'Gadgets': False, 'World News': False}


#publish data
def publish(topic, data):
    if publishedData.__contains__(topic):
        exData = publishedData[topic]
        newData = exData + ',' + data
    else:
        newData = data
    publishedData[topic] = newData
    notifyUsers[topic] = True
    if subscribedData.__contains__(topic):
        userList = subscribedData[topic]
        for user in userList:
            subscribedUser[user] = True
    publishedDataDb.delete_many({})
    UpdatedpublishData = {'publishedData':publishedData}
    publishedDataDb.insert_one(UpdatedpublishData)
    print(notifyUsers)


#subscribe data
def subscribe(topic, username):
    newUser = list()
    if subscribedData.__contains__(topic):
        exUsername = subscribedData[topic]
        if not exUsername.__contains__(username):
            newUser = exUsername
            newUser.append(username)
    else:
        newUser.append(username)
    subscribedData[topic] = newUser


#notify users
def notify(user):
    users = list()
    for topic in topics:
        if notifyUsers.__contains__(topic):
            if notifyUsers[topic]:
                if subscribedData.__contains__(topic):
                    if subscribedData[topic].__contains__(user):
                        return True
    return False


#fetch data from mongodb
def CallDb():
    print("callDb called")
    dbEntry = publishedDataDb.find_one()
    publishedData = dbEntry['publishedData']
    print("From db ")
    print(publishedData)
    return publishedData


@app.route("/", methods=['GET', 'POST'])
def index():
    #called while logging in
    if request.method == 'POST' and 'userName' in request.form:
        print(request.form.get('userName'))
        user = request.form.get('userName')
        subscribedUser[user] = True
        return 'success'
    #called while publishing data
    if request.method == 'POST' and 'Topics' in request.form:
        topic = request.form.get('Topics')
        data = request.form.get('Data')
        publish(topic, data)
        return 'success'
    #called when subscribing to data
    if request.method == 'POST' and 'subtopics' in request.form:
        print("i am here subtopics")
        username = request.form.get('subusername')
        subscription = request.form.get('subtopics')
        subscribe(subscription, username)
        subscribedUser[username] = True
        print(subscribedData)
        return 'success'
    #called when updating subscribed topics
    if request.method == 'POST' and 'subscribed_user' in request.form:
        subUser = request.form.get('subscribed_user')
        print('finding users')
        pubData = ''
        for topic in topics:
            if subscribedData.__contains__(topic):
                userList = subscribedData[topic]
                print(userList)
                publishedData = CallDb()
                if userList.__contains__(subUser) and publishedData.__contains__(topic):
                    publishedData_val = publishedData[topic].split(",")
                    for value in publishedData_val:
                        content = 'Update from ' + topic + ' : ' + value + '\n'
                        pubData += content
        return pubData
    #called when new data is published to notify users
    if request.method == 'POST' and 'notify_user' in request.form:
        user = request.form.get('notify_user')
        userList = notify(user)
        if userList:
            print('found user for notif')
            notif = 'There is a new notification'
            return notif
        else:
            print('user not found')
            return ''
    if request.method == 'POST' and 'user_notif' in request.form:
        print('in user_notif')
        user = request.form.get('user_notif')
        print(user)
        for topic in topics:
            if (subscribedData.__contains__(topic) and notifyUsers[topic]) and subscribedUser[user] == True :
                users = subscribedData[topic]
                if users.__contains__(user):
                    print("FOUND!!!!!!")
                    subscribedUser[user] = False
                    return 'true'
        return 'false'
    else:
        return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
