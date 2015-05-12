# set username and password values
USERNAME = 'jied314'
PASSWORD = 'Hotmail8'
USER_AGENT = 'how to ask for a favor by /u/_Jie_'
ROAP = 'Random_Acts_Of_Pizza'
QUERY_LIMIT = 100

# time frame
START_2011 = 1293840000.0
START_2012 = 1325376000.0
START_2013 = 1356998400.0
START_2014 = 1388534400.0
DAY_SECONDS = 86400.0
WEEK_SECONDS = DAY_SECONDS * 7
MONTH_SECONDS = DAY_SECONDS * 30
QUARTER_SECONDS = MONTH_SECONDS * 3
YEAR_SECONDS = DAY_SECONDS * 365

#
FILE_NAME = 'roap_info.txt'
count = 0
THRESHOLD = 1000
OUT_FILE = 'data/data.csv'
SUCCESS_FILE = 'data/success.txt'
NOT_SUCCESS_FILE = 'data/not_success.txt'

# set db values
DB_NAME = "roap.db"
RAW_ROAP_TABLE_NAME = "raw_roap"
ROAP_TABLE_NAME = "roap"

INTEGER_TYPE = "INTEGER"
BOOLEAN_TYPE = "INTEGER"
LONG_TYPE = "INTEGER"
FLOAT_TYPE = "REAL"
STRING_TYPE = "TEXT"
BINARY_TYPE = "BLOB"
NULL_TYPE = "NULL"

raw_story_primary_key = 'name'
raw_story_primary_key_type = STRING_TYPE

# raw story fields dictionary (33)
RAW_FIELDS_DICT = {'approved_by':   STRING_TYPE,  'archived': STRING_TYPE,  'author':      STRING_TYPE,
                   'clicked':       BOOLEAN_TYPE, 'created':  FLOAT_TYPE,   'created_utc': FLOAT_TYPE,
                   'distinguished': STRING_TYPE,  'domain':   STRING_TYPE,  'downs':       INTEGER_TYPE,
                   'edited':        FLOAT_TYPE,   'gilded':   INTEGER_TYPE, 'hidden':      BOOLEAN_TYPE,
                   'id':            STRING_TYPE,  'is_self':  BOOLEAN_TYPE, 'likes':       BOOLEAN_TYPE,
                   'link_flair_css_class': STRING_TYPE, 'link_flair_text': STRING_TYPE,
                   'num_comments':  INTEGER_TYPE, 'num_reports':  INTEGER_TYPE,
                   'over_18':       BOOLEAN_TYPE, 'permalink':    STRING_TYPE,  'saved':         BOOLEAN_TYPE,
                   'score':         INTEGER_TYPE, 'selftext':     STRING_TYPE,  'selftext_html': STRING_TYPE,
                   'stickied':      BOOLEAN_TYPE, 'subreddit':    STRING_TYPE,  'subreddit_id':  STRING_TYPE,
                   'thumbnail':     STRING_TYPE,  'title':        STRING_TYPE,  'ups':           INTEGER_TYPE,
                   'url':           STRING_TYPE}


story_label = 'label'
story_label_type = STRING_TYPE
THANKS = 'thanks'
REQUEST = 'request'
OTHERS = 'others'
SUCCESS = 'got_pizza'
NOT_SUCCESS = 'no_pizza'
HYPERLINK_FEATURE = 'http'


intermediate_story_primary_key = 'name'  # name
intermediate_story_primary_key_type = STRING_TYPE

# intermediate story fields dictionary (prepare data)
INTERMEDIATE_FIELDS_DICT = {
    story_label: story_label_type,
    'giver_username': STRING_TYPE,
    'author': STRING_TYPE,
    'edited': INTEGER_TYPE,
    'num_comments': INTEGER_TYPE,
    'score':        INTEGER_TYPE,
    'ups':   INTEGER_TYPE,
    'downs': INTEGER_TYPE,
    'title': STRING_TYPE,
    'selftext':  STRING_TYPE,
    'text_length': INTEGER_TYPE,
    'link_provided': INTEGER_TYPE,
    'created':  FLOAT_TYPE,
    'created_utc':    FLOAT_TYPE,
}


# rename fields to be easy understandable
FIELD_NAME_DICT = {
    'label':  'receive_pizza_or_not',
    'name':   'request_id',
    'author': 'requester_username',
    'edited': 'request_was_edited',
    'num_comments': 'request_num_comments_received_at_retrieval',
    'score': 'request_num_upvotes_minus_downvotes',
    'ups':   'request_num_upvotes',
    'downs': 'request_num_downvotes',
    'selftext': 'request_text',
    'title':    'request_title',
    'created':  'unix_timestamp_local_of_request',
    'created_utc': 'unix_timestamp_utc_of_request'
}


# intermediate story fields dictionary (prepare data)
INTERMEDIATE_ELIGIBLE_FIELDS_DICT = {
    story_label: story_label_type,
    'giver_username': STRING_TYPE,
    'requester_username': STRING_TYPE,  # author
    'request_was_edited': INTEGER_TYPE, # edited
    'request_num_comments_received_at_retrieval': INTEGER_TYPE,  # num_comments
    'request_num_upvotes_minus_downvotes':        INTEGER_TYPE,  # score
    'request_num_upvotes':   INTEGER_TYPE,  # ups
    'request_num_downvotes': INTEGER_TYPE,  # downs
    'request_text':  STRING_TYPE,  # selftext
    'request_title': STRING_TYPE,  # title
    'unix_timestamp_local_of_request':  FLOAT_TYPE,  # created
    'unix_timestamp_utc_of_request':    FLOAT_TYPE,  # created_utc
}



