from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cnf1miou0vdt9d1qe8sx164zejp3fnay'

topics = ['Football', 'Movies', 'TV Shows', 'Gadgets', 'World News']
publishedData = dict()
subscribedUser = dict()
subscribedData = dict()
username = list()
notifyUsers = {'Football' : False, 'Movies' : False, 'TV Shows' : False, 'Gadgets' : False, 'World News' : False}


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
    print(notifyUsers)


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


def notify():
    users = list()
    for topic in topics:
        if notifyUsers.__contains__(topic):
            if notifyUsers[topic]:
                if subscribedData.__contains__(topic):
                    users = subscribedData[topic]
    return users


# Basic flask call to start web app
@app.route("/", methods = ['GET', 'POST'])
def index():
    if request.method == 'POST' and 'userName' in request.form:
        print(request.form.get('userName'))
        user = request.form.get('userName')
        subscribedUser[user] = True
        return 'success'
    if request.method == 'POST' and 'Topics' in request.form:
        topic = request.form.get('Topics')
        data = request.form.get('Data')
        publish(topic, data)
        print(publishedData)
        return 'success'
    if request.method == 'POST' and 'subtopics' in request.form:
        print("i am here subtopics")
        username = request.form.get('subusername')
        subscription = request.form.get('subtopics')
        subscribe(subscription, username)
        subscribedUser[username] = True
        print(subscribedData)
        return 'success'
    if request.method == 'POST' and 'subscribed_user' in request.form:
        subUser = request.form.get('subscribed_user')
        print('finding users')
        pubData = ''
        for topic in topics:
            if subscribedData.__contains__(topic):
                userList = subscribedData[topic]
                print(userList)
                if userList.__contains__(subUser) and publishedData.__contains__(topic):
                    publishedData_val = publishedData[topic].split(",")
                    for value in publishedData_val:
                        content = 'Update from ' + topic + ' : ' + value + '\n'
                        pubData += content
        return pubData
    if request.method == 'POST' and 'notify_user' in request.form:
        userList = notify()
        print(userList)
        user = request.form.get('notify_user')
        print(user)
        for exUser in userList:
            if exUser == user:
                print('found user for notifying')
                notif = 'There is a new notification'
                return notif
        else:
            print('user not found')
            return ''
    if request.method == 'POST' and 'user_notif' in request.form:
        user = request.form.get('user_notif')
        print(user)
        for topic in topics:
            if (subscribedData.__contains__(topic) and notifyUsers[topic]) and subscribedUser[user]==True :
                users = subscribedData[topic]
                if users.__contains__(user):
                    print("FOUND!!!!!!")
                    subscribedUser[user] = False
                    return 'true'
        return 'false'
    else:
        return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',threaded=True, port=8081)
