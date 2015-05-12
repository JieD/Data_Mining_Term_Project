import sqlite3
import csv
import codecs
import cStringIO
import db_client


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def test():
    conn = sqlite3.connect('yourdb.sqlite')
    c = conn.cursor()
    c.execute('select * from yourtable')
    writer = UnicodeWriter(open("export.py.csv", "wb"))
    writer.writerows(c)


def write(conn, table_name, csv_file_name, column_list):
    columns = db_client.parse_column_list(column_list)
    cursor = conn.cursor()
    data = cursor.execute("SELECT {cns} FROM {tn}".format(cns=columns, tn=table_name))
    writer = UnicodeWriter(open(csv_file_name, "wb"))
    writer.writerows(data)


def write(conn, table_name, csv_file_name, *args):
    columns = db_client.combine_columns(*args)
    cursor = conn.cursor()
    data = cursor.execute("SELECT {cns} FROM {tn}".format(cns=columns, tn=table_name))
    writer = UnicodeWriter(open(csv_file_name, "wb"))
    writer.writerow(args)
    writer.writerows(data)
