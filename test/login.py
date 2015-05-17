# This script login to reddit API with given username and password.

from pprint import pprint
import requests
import json

#set username and password values
username = 'jied314'
password = 'Hotmail8'

#create dict with username and password
user_pass_dict = {'user': username,
                  'passwd': password,
                  'api_type': 'json'}

#set the header for all the following requests
headers = {'user-agent': 'data mining of ROAP', }

#create a requests.session that'll handle our cookies for us
client = requests.session()
client.headers = headers

#make a login request, passing in the user and pass as data
r = client.post(r'http://www.reddit.com/api/login', data=user_pass_dict)

#optional print to confirm error-free response
pprint(r.text)

#turns the response's JSON to a native python dict
j = json.loads(r.text)

#grabs the modhash from the response
client.modhash = j['json']['data']['modhash']

#prints the users modhash
print '{USER}\'s modhash is: {mh}'.format(USER=username, mh=client.modhash)

#r = requests.get(r'http://www.reddit.com/user/jied314/comments/.json')
#j = json.loads(r.text)  #turn the json response into a python dict
#j = r.json() # or use built-in jason
#pprint(j)  #here's the final response, printed out in nicely readable format
#for child in j['data']['children']:
#    print child['data']['id'], "\r\n", child['data']['author'],child['data']['body']
#    print