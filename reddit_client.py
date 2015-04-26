import json
import requests
from pprint import pprint as pp2
import lib
import time


# login using provided username, password and user agent
def login(username, password, user_agent):
    """logs into reddit, saves cookie"""

    print 'begin log in'

    # username and password
    UP = {'user': username, 'passwd': password, 'api_type': 'json'}
    headers = {'user-agent': user_agent}

    # POST with user/pwd
    client = requests.session()
    client.headers = headers

    r = client.post('http://www.reddit.com/api/login', data=UP)

    #print r.text
    #print r.cookies

    # gets and saves the modhash
    j = json.loads(r.text)

    client.modhash = j['json']['data']['modhash']
    print '{USER}\'s modhash is: {mh}'.format(USER=username, mh=client.modhash)
    client.user = username

    def name():
        return '{}\'s client'.format(username)

    pp2(j)
    return client


# query stories using the passed in parameters to form request
def query_stories(client, limit=lib.QUERY_LIMIT, sr='Random_Acts_Of_Pizza', sorting='new', **kwargs):
    """retrieves X (max 100) amount of stories in a subreddit\n
    'sr' the subreddit from which to get story, can concatenate using '+'
    'sorting' is whether or not the sorting of the reddit should be customized or not,
    new, top or hot. if it is: Allowed passing params/queries such as t=hour, week, month, year or all
    '**kwargs' set extra parameters, e.g. before & after"""

    # query to send
    parameters = {'limit': limit}

    # parameters= defaults.copy()
    parameters.update(kwargs)

    url = r'http://www.reddit.com/r/{sr}/{top}.json'.format(sr=sr, top=sorting)
    r = client.get(url, params=parameters)
    print 'sent URL is', r.url
    j = json.loads(r.text)

    #print '\nstart printing json'
    #pp2(j)
    #print 'finish printing json\n'
    return j


# query stories using search within timestamp
# regular query only returns the latest 1000 stories
def query_stories_in_time_range(client, start_time, end_time, sr='Random_Acts_Of_Pizza', sorting='new',
                                limit=lib.QUERY_LIMIT, **kwargs):
    parameters = {'sort': sorting, 'limit': limit, 'restrict_sr': 'on', 'syntax': 'cloudsearch'}
    parameters.update(kwargs)
    url = r'http://www.reddit.com/r/{sr}/search.json?q=timestamp:{st}..{et}'.format(sr=sr, st=int(start_time),
                                                                                    et=int(end_time))
    r = client.get(url, params=parameters)
    print 'sent URL is', r.url
    j = json.loads(r.text)
    return j


# the http response contain after and before information
def get_name_range(json_stories):
    j = json_stories['data']
    after_name = j['after']
    before_name = j['before']
    return [after_name, before_name]


def parse_stories(json_stories, return_json=False):
    """return_json - whether return json or a list of stories"""
    if return_json:  # return raw json
        return json_stories
    else:  # return a list of stories
        stories = []
        if json_stories:  # check if stories is empty
            for story in json_stories['data']['children']:
                stories.append(story['data'])
            #pp2(story)
            #print 'name: ', story['data']['name']
        #print 'number of stories is: {0}'.format(str(len(stories)))

        #data = stories[0]['data']
        # pp2(data)
        #created = data['created']
        #edited = data['edited']
        #pp2(edited)
        #print '{0}'.format(isinstance(edited, bool))
        return stories


def first_query(client, sr):
    json_stories = query_stories(client, limit=1, sr=sr)
    stories = parse_stories(json_stories)
    return stories[len(stories) - 1]


def main():
    client = login(lib.USERNAME, lib.PASSWORD, lib.USER_AGENT)
    start_time = 1429330959
    end_time = time.time()
    after_name = ''
    while True:
        json_stories = query_stories_in_time_range(client, start_time, end_time, limit=10, after=after_name)
        j = parse_stories(json_stories)
        length = len(j)
        if length == 10:
            after_name = j[length - 1]['name']
        else:
            break

    #json_stories = query_stories(client, limit=2)
    #parse_stories(json_stories)
    #pp2(first_query(client, lib.ROAP))


if __name__ == "__main__":
    main()
