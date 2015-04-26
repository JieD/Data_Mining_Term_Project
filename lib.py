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

#
FILE_NAME = 'roap_info.txt'
count = 0
THRESHOLD = 1000

# set db values
DB_NAME = "roap.db"
RAW_ROAP_TABLE_NAME = "raw_roap"

INTEGER_TYPE = "INTEGER"
BOOLEAN_TYPE = "INTEGER"
LONG_TYPE = "INTEGER"
FLOAT_TYPE = "REAL"
STRING_TYPE = "TEXT"
BINARY_TYPE = "BLOB"
NULL_TYPE = "NULL"

STORY_FIELDS_DICT = {'approved_by':   STRING_TYPE,  'archived': STRING_TYPE,  'author':      STRING_TYPE,
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
story_primary_key = 'name'
story_primary_key_type = STRING_TYPE

FIELDS_DICT = {
    'giver_name': STRING_TYPE, 'requester_id': STRING_TYPE, 'requester_name': STRING_TYPE,
}