import tweepy
import json

consumer_key = <your consumer key>
consumer_secret = <your consumer secret>
access_token = <your access token>
access_secret = <your access secret>

# set OAuth handler for Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)


@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status


# Status() is the data model for a tweet
tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse


class MyListener(tweepy.streaming.StreamListener):

    def on_data(self, data):
        try:
            decoded = json.loads(data)
            if not decoded['text'].startswith('RT'):  # filters out retweets
                with open('../data/input/twitterdata_indonesia.json', 'a', encoding='utf-8', newline='') as f:
                    f.write(data)
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        print(status)
        return True


# Set the hashtag/query to be searched in track
subtopic = ['riot', 'protest', 'election violence', 'violence against civilians']
twitter_stream = tweepy.Stream(auth, MyListener())
twitter_stream.filter(track=subtopic, languages=['en'], locations=[106,-6,120,5])