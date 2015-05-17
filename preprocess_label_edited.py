import sqlite3
import re
import lib
import db_client
import export
from pprint import pprint as pp2


# assign preliminary label (thanks, request, others)
def assign_priliminary_label(cursor, source, destination):
    source_id_column = lib.raw_story_primary_key
    destination_id_column = lib.intermediate_story_primary_key
    cursor = db_client.select_all(cursor, source, source_id_column, 'title', 'author', 'created', 'created_utc')
    all_rows = cursor.fetchall()

    i = 0
    for row in all_rows:
        name = row[0]
        title = row[1]
        label = check_title(title)
        title = drop_tag(title)
        author = row[2]
        created = row[3]
        created_utc = row[4]

        # insert request & thanks into destination
        if label is not lib.OTHERS:
            i += 1
            db_client.insert_id(cursor, destination, destination_id_column, name)
            db_client.update(cursor, destination, destination_id_column, name, lib.story_label, label)
            db_client.update(cursor, destination, destination_id_column, name, 'author', author)
            db_client.update(cursor, destination, destination_id_column, name, 'title', title)
            db_client.update(cursor, destination, destination_id_column, name, 'created', created)
            db_client.update(cursor, destination, destination_id_column, name, 'created_utc', created_utc)
    print "Retrieve {0} requests & thanks".format(i)


# check the tag information in the title
# if thanks, then the author got a pizza
# if not request nor thanks, then we are not interested
def check_title(title):
    first_word = title.split()[0]  # tag
    #pp2(first_word)
    if 'request' not in first_word.lower():
        if 'thanks' in first_word.lower():
            #pp2(title)
            return lib.THANKS  # got pizza
        else:
            return lib.OTHERS  # not interested
    else:
        return lib.REQUEST  # request


# drop the tag in the title
def drop_tag(title):
    words = title.split()[1:]
    return ' '.join(words)


# parse the title to find giver - TODO
def find_giver(title):
    return ''


# find matching thanks & requests
# find all thanks
# for each thanks:
#   find all the posts (before the post time) made by the author
#   the closest one is the request that is fulfilled
#   delete this thanks
#   if zero request found, probably the author participate in an offer story and won
def match_thanks_request(cursor):
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    time_column = 'created'
    author_column = 'author'
    label_column = lib.story_label

    # get all thanks
    cursor = db_client.select_condition(cursor, table_name, lib.story_label, lib.THANKS, time_column,
                                        id_column, author_column, time_column)
    all_rows = cursor.fetchall()

    # find the matching request
    zero_match = 0
    num_success = 0
    for row in all_rows:
        thanks_name = row[0]
        author = row[1]
        created_utc = row[2]
        start_time = created_utc - lib.QUARTER_SECONDS  # give one month period
        end_time = created_utc - 1

        # find all requests made by the author within the time period, order by post time
        columns = db_client.combine_columns(id_column, author_column, time_column)
        cursor = cursor.execute("SELECT {cns} FROM {tn} WHERE {cn1}=? AND {cn2}=? AND {cn3} BETWEEN (?) AND (?) ORDER BY {oc} ASC".
                                format(cns=columns, tn=table_name, cn1=author_column, cn2=label_column, cn3=time_column, oc=time_column),
                                (author, lib.REQUEST, start_time, end_time,))
        stories = cursor.fetchall()
        num_requests = len(stories)
        if num_requests > 0:
            story = stories[num_requests - 1]  # the latest request is the one
            request_name = story[0]
            db_client.update(cursor, table_name, id_column, request_name, label_column, lib.SUCCESS)  # update label
            #if num_requests > 1:
            #    print "{0}: {1} - {2} - {3}".format(story[0], story[1], num_requests, story[2])
            num_success += 1
        else:
            zero_match += 1

        # delete thanks
        db_client.delete(cursor, table_name, id_column, thanks_name)
    print "total number of thanks: {}".format(zero_match + num_success)
    print "number of zero match thanks: {}".format(zero_match)
    print "number of preliminary success: {}".format(num_success)


# debugging method to check label result
def test(cursor, author):
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    time_column = 'created'
    author_column = 'author'
    cursor = db_client.select_condition(cursor, table_name, author_column, author, time_column, id_column,
                                        'title', 'edited', 'selftext', lib.story_label)
    all_rows = cursor.fetchall()

    i = 0
    for row in all_rows:
        i += 1
        print '\nid: {0}\ntitle: {1}\nedited: {2}'.format(row[0], row[1], row[2])
        print "-----------------------------"
        print '{0}\nlabel: {1}'.format(row[3], row[4])
        print "-----------------------------"
    print "\nnumber of posts: {0}".format(i)


# change not successful request label
def label_unsuccessful_request(cursor, table_name):
    label_column = lib.story_label
    id_column = lib.intermediate_story_primary_key
    cursor = db_client.select_condition_no(cursor, table_name, label_column, lib.REQUEST, id_column)
    all_rows = cursor.fetchall()

    i = 0
    for row in all_rows:
        i += 1
        name = row[0]
        db_client.update(cursor, table_name, id_column, name, label_column, lib.NOT_SUCCESS)
    print "number of preliminary not success: {}".format(i)


# if a user has more than one requests, only save the earliest one
def choose_first_request(cursor, table_name):
    id_column = lib.intermediate_story_primary_key
    author_column = 'author'
    usernames = db_client.get_distinct_values(cursor, table_name, author_column)
    for username in usernames:
        cursor = db_client.select_condition(cursor, table_name, author_column, username, 'created', id_column)
        all_rows = cursor.fetchall()

        request_counts = len(all_rows)
        if request_counts > 1:
            for row in all_rows[1:]:
                name = row[0]
                db_client.delete(cursor, table_name, id_column, name)


# copy the rest fields from raw to intermediate table
def cpy_rest(cursor, source, destination):
    source_id_column = lib.raw_story_primary_key
    destination_id_column = lib.intermediate_story_primary_key
    columns = ['edited', 'num_comments', 'score', 'ups', 'downs', 'selftext']

    cursor = db_client.select_all(cursor, destination, destination_id_column)
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        # sqlite3 - why not support copy between tables? - TODO
        #db_client.cpy_columns(cursor, source, destination, columns, columns, source_id_column, name)
        for column in columns:
            cursor = db_client.select_condition_no(cursor, source, source_id_column, name, column)
            row = cursor.fetchone()
            value = row[0]
            db_client.update(cursor, destination, destination_id_column, name, column, value)
    update_edited(cursor, destination)  # get preliminary edit status


# extract edits (if there are) for labeling purpose
def extract_edit_sentences(cursor, table_name, id_column, label, file_name):
    out_file = open(file_name, 'w')
    out_file.write("Edit sentences for table = {0}, label = {1}\n\n".format(table_name, label))
    cursor = db_client.select_condition(cursor, table_name, lib.story_label, label, 'created_utc', id_column, 'selftext')
    all_rows = cursor.fetchall()
    for row in all_rows:
        name = row[0]
        text = row[1]
        text = unicode(text).encode("utf-8")  # avoid encoding error (Unicode & ASCII)
        left_text = extract_edit(name, text, out_file).decode("utf-8")
        db_client.update(cursor, table_name, id_column, name, 'edit_remove_text', left_text)


# extract sentences containing edit and write to out_file
# steps:
# 1. check if contains edit
# 2. if contain edits, find all paragraphs containing edits; else, return empty string
# 3. for each paragraph containing edits, only keep the sentences came after edit, and write to out_file
def extract_edit(name, text, out_file):
    final_text = ""
    edit = re.compile(r'\b(edit)\b', re.I)
    edit_start = False

    if edit.search(text) is not None:  # contain edit
        #print name
        out_file.write("{0}\n".format(name))
        paragraphs = text.split('\n')
        for paragraph in paragraphs:  # extract the paragraph containing edit, but only start with sentences containing edit
            if edit.search(paragraph):  # paragraph contains edit
                edit_sents = []
                for sent in lib.sent_detector.tokenize(paragraph.strip(), realign_boundaries=True):
                    if edit_start or edit.search(sent) is not None:
                        edit_start = True
                        edit_sents.append(sent)  # only interested in sentences came after edit
                        #print sent
                        out_file.write(sent + '\n')
                    else:
                        final_text += sent  # sentence not contains edit
            else:
                final_text += (paragraph + '\n')  # paragraph not contains edit
        #print
        out_file.write("\n")
        return final_text
    else:
        return text


# read the label got from edits, and print result
# edits for different requests are separated by empty lines
# edits are in the following format:
#     label
#     id
#     valid edits (if any)
def read_labeled_edits(cursor, table_name, id_column, file_name):
    num_success = 0
    num_outliers = 0
    in_file = open(file_name, 'r')
    line = in_file.readline()
    while line != '':
        edits = []
        while line != '\r\n' and line != '':  # read all sentences between empty lines
            edits.append(line.strip())
            line = in_file.readline()
        label = int(edits[0])
        name = edits[1]
        edit_sents = edits[2:]
        if len(edit_sents) > 0:  # add request edits back
            edits = ' '.join(edit_sents).decode("utf-8")
            edits_remove = db_client.select_condition_no(cursor, table_name, id_column, name, 'edit_remove_text').fetchone()[0]
            request_text = edits_remove + edits
            db_client.update(cursor, table_name, id_column, name, 'edit_remove_text', request_text)
        else:  # update edit status to 0
            db_client.update(cursor, table_name, id_column, name, 'edited', 0)

        if label == 1:  # change label to success
            num_success += 1
            #print name, '\n'
            db_client.update(cursor, table_name, id_column, name, lib.story_label, lib.SUCCESS)
        elif label == -1:  # remove outliers
            num_outliers += 1
            #print name, '\n'
            db_client.delete(cursor, table_name, id_column, name)

        line = in_file.readline()
    # EOF
    in_file.close()
    print "{0}\nnumber of success: {1}\nnumber of outliers: {2}".format(file_name, num_success, num_outliers)


# replace selftext with edit_remove_text
def update_selftext(cursor, table_name, id_column):
    cursor = db_client.select_all(cursor, table_name, id_column, 'edit_remove_text')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        edits = row[1]
        db_client.update(cursor, table_name, id_column, name, 'selftext', edits)


# if request body is empty, use title. (only for text analysis purpose)
def treat_empty_text(cursor, table_name, id_column):
    cursor = db_client.select_condition_no(cursor, table_name, 'edit_remove_text', '', id_column, 'title')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        title = row[1]
        db_client.update(cursor, table_name, id_column, name, 'edit_remove_text', title)


#def priliminary_text_analysis():


# update edited to 1 or 0
def update_edited(cursor, destination):
    destination_id_column = lib.intermediate_story_primary_key
    edited_column = 'edited'

    cursor = db_client.select_all(cursor, destination, destination_id_column, edited_column)
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        edited = row[1]
        if edited > 0.0:  # has been edited
            edited = 1
        db_client.update(cursor, destination, destination_id_column, name, edited_column, edited)


# create intermediate table to store filtered attributes
def create_intermediate_table(cursor, table_name):
    db_client.create_story_table(cursor, table_name, lib.intermediate_story_primary_key,
                                 lib.intermediate_story_primary_key_type, lib.INTERMEDIATE_FIELDS_DICT)


def label_count(cursor, table_name):
    label_column = lib.story_label
    success_count = db_client.count(cursor, table_name, label_column, lib.SUCCESS)
    not_success_count = db_client.count(cursor, table_name, label_column, lib.NOT_SUCCESS)
    print "\nin table {0}:\nnumber of success: {1}\nnumber of not success: {2}".format(table_name, success_count, not_success_count)


def main():
    # init
    conn = sqlite3.connect(lib.DB_NAME)
    source_name = lib.RAW_ROAP_TABLE_NAME
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    db_client.delete_table(cursor, table_name)
    create_intermediate_table(cursor, table_name)

    assign_priliminary_label(cursor, source_name, table_name)
    match_thanks_request(cursor)
    label_unsuccessful_request(cursor, table_name)
    cpy_rest(cursor, source_name, table_name)
    #test(cursor, '')

    #choose_first_request(cursor, table_name)

    print '\nextract edits\n'
    extract_edit_sentences(cursor, table_name, id_column, lib.NOT_SUCCESS, lib.EDIT_NOT_SUCCESS_FILE)
    extract_edit_sentences(cursor, table_name, id_column, lib.SUCCESS, lib.EDIT_SUCCESS_FILE)

    print 'read labels:'
    read_labeled_edits(cursor, table_name, id_column, lib.LABELED_EDIT_NOT_SUCCESS)
    read_labeled_edits(cursor, table_name, id_column, lib.LABELED_EDIT_SUCCESS)
    #test(cursor, 'Franklyidontgivearip')

    #update_selftext(cursor, table_name, id_column)
    treat_empty_text(cursor, table_name, id_column)

    label_count(cursor, table_name)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()