import pprint
import praw
import time
import schedule
import warnings
import sys
import os
from configparser import ConfigParser
sys.tracebacklimit=0
MESSAGE_SUBJECT = "TheMessageBot Subreddits"
config = ConfigParser()
config.read('config.ini')

client_id = config.get('reddit', 'CLIENT_ID')
client_secret = config.get('reddit', 'CLIENT_SECRET')
username = config.get('reddit', 'USERNAME')
password = config.get('reddit', 'PASSWORD')

def reddit_instance():
    reddit = praw.Reddit(client_id=client_id,\
        client_secret =client_secret,\
        user_agent = "Message Bot",\
        username = username,\
        password = password)
    return reddit


print("Bot is running under the User: {}".format(reddit_instance().user.me()))
def main_job():
    reddit = reddit_instance()
    inbox = reddit.inbox.unread(limit = None)
    for message in inbox:
        if isinstance(message, praw.models.Message):
            text = message.body
            user = str(message.author)
            subject = str(message.subject).strip()
            if subject == MESSAGE_SUBJECT:
                subreddits = text.split(",")
                for response in subreddits:
                    given = response.split()
                    subreddit = str(given[0].split("/")[1]).strip()
                    return_type = str(given[1]).strip()
                    number = int(given[2])
                    try:
                        if return_type == "top":
                            posts = reddit.subreddit(subreddit).top(time_filter = "day", limit = number)
                        elif return_type == "new":
                            posts = reddit.subreddit(subreddit).new(limit = number)
                        elif return_type == "hot":
                            posts = reddit.subreddit(subreddit).hot(limit = number)
                        elif return_type == "rising":
                            posts = reddit.subreddit(subreddit).rising(limit = number)
                        elif return_type == "controversial":
                            posts = reddit.subreddit(subreddit).controversial(limit = number)
                        posts_dict = list()
                        for post in posts:
                            temp = [post.title, post.url]
                            posts_dict.append(temp)
                        send_message(posts_dict, user, message, str(subreddit), return_type)
                    except Exception as e:
                        send_message("Invalid subreddit or Invalid type {}\n".format(return_type), user, message)
                        continue
            else:
                temp = "Your request has not been handled. Make sure you have enterered correct Subject\n"
                send_message(temp, user, message)
        message.mark_read()


def send_message(body, username, instance, subreddit = None, return_type = None):
    reddit = reddit_instance()
    if(isinstance(body, list)):
        message = "Here are the {} {} posts of the day from {} subreddit:\n".format(return_type, len(body), subreddit)
        message += "\n"
        for i, b in enumerate(body):
            i = i+1
            message += str(i) + "."
            message += "Title - {}\n".format(b[0])
            message += "\n"
            message += "url - {}\n".format(b[1])
            message += "\n"
    else:
        message = body
        message += "\n"

    message += "Your replies here will be ignored as this is an automated message.\n"
    if instance.author == username:
        instance.reply(message)

while True:
    main_job()