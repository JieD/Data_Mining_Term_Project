import json
import requests
from pprint import pprint as pp2
import lib


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
def query_stories(client, limit=100, sr='Random_Acts_Of_Pizza', sorting='', **kwargs):
    """retrieves X (max 100) amount of stories in a subreddit\n
    'sr' the subreddit from which to get story, can concatenate using '+'
    'sorting' is whether or not the sorting of the reddit should be customized or not,
    new, top or hot. if it is: Allowed passing params/queries such as t=hour, week, month, year or all
    'return_json' whether return json or a list of stories
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


def get_name_range(json_stories):
    j = json_stories['data']
    after_name = j['after']
    before_name = j['before']
    return [after_name, before_name]


def parse_stories(json_stories, return_json=False):
    count = 0

    if return_json:  # return raw json
        return json_stories
    else:  # return a list of stories
        stories = []
        for story in json_stories['data']['children']:
            stories.append(story['data'])
            #pp2(story)
            print
            count += 1
        print 'number of stories is: {COUNT}'.format(COUNT=count)

        #data = stories[0]['data']
        # pp2(data)
        #created = data['created']
        #edited = data['edited']
        #pp2(edited)
        #print '{0}'.format(isinstance(edited, bool))
        return stories


def main():
    client = login(lib.USERNAME, lib.PASSWORD, lib.USER_AGENT)
    json_stories = query_stories(client, limit=1)
    return parse_stories(json_stories)


if __name__ == "__main__":
    main()
