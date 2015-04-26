import sqlite3

# if the database is already created, connect to it instead of making a new one
conn = sqlite3.connect('test.db')
print "Opened database successfully";

with conn:
    cursor = conn.cursor()

    # create a table
    cursor.execute("""CREATE TABLE books (title text, author text)""")

    # insert some data
    cursor.execute("INSERT INTO books VALUES ('Pride and Prejudice', 'Jane Austin')")

    # save data to db
    conn.commit()

    # insert multiple records using the more secure "?" method
    books = [('Harry Potter', 'J.K Rowling'),
             ('The Lord Of the Rings', 'J. R. R. Tolkien'),
             ('The Hobbit', 'J. R. R. Tolkien')]
    cursor.executemany("INSERT INTO books VALUES (?,?)", books)

    # update data
    sql = """UPDATE books SET author = 'Yasoob' WHERE author = 'J.K Rowling'"""

    # delete data
    sql = """DELETE FROM books WHERE author = 'Yasoob'"""
    cursor.execute(sql)
    conn.commit()

cursor = conn.execute("SELECT title, author from books")
for row in cursor:
    print "Title = ", row[0]
    print "Author = ", row[1], "\n"
print "Operation done successfully"
conn.close()







