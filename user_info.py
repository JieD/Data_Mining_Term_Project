from pprint import pprint
import json
import lib
import reddit_client

client = reddit_client.login(lib.USERNAME, lib.PASSWORD, lib.USER_AGENT)
#parameters = {'sort': 'new', 'limit': 100, 'restrict_sr': 'on', 'syntax': 'cloudsearch'}
#url = r'http://www.reddit.com/user/{un}/about/.json'.format(un='thanks')
url = r'http://www.reddit.com/search.json?q=subreddit:Random_Acts_Of_Pizza+author:the'
r = client.get(url)
print 'sent URL is', r.url
j = json.loads(r.text)
pprint(j)
#comments = j['data']['children']
#num_comment = len(comments)
#print "user has {0} comments".format(num_comment)
#print data['comment_karma'], "\r\n", data['link_karma'], data['created'], data['created_utc']

def is_user_name(name):
    client = reddit_client.login(lib.USERNAME, lib.PASSWORD, lib.USER_AGENT)
    url = r'http://www.reddit.com/search.json?q=subreddit:Random_Acts_Of_Pizza+author:{0}'.format(name)
    r = client.get(url)
    print 'sent URL is', r.url
    j = json.loads(r.text)
