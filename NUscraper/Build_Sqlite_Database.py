import os
import time
import sqlite3

def create_project(conn, project):
    # create table
    sql = '''CREATE TABLE URLS (Title, URL, Description, Pubdate, Permlink, Image, Cat1, Cat2, Cat3, Cat4, Cat5, Cat6, Cat7, Cat8, Cat9, Creator, Rights, RSSFeed, IsCollected)'''
    insert = '''INSERT INTO URLS VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql)
    cur.execute(insert, project)

def extend_project(conn, project):
    sql = '''INSERT INTO URLS (Title, URL, Description, Pubdate, Permlink, Image, Cat1, Cat2, Cat3, Cat4, Cat5, Cat6, Cat7, Cat8, Cat9, Creator, Rights, RSSFeed, IsCollected) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)

def database_main(db, dbinfo):
    if os.path.exists(db) == True:
        # create a database connection
        with sqlite3.connect(db) as conn:
            # extend the project
            extend_project(conn, dbinfo)
    else:
        with sqlite3.connect(db) as conn:
            create_project(conn, dbinfo)

def database_search_links(db, searchword):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM URLS WHERE Permlink = ? COLLATE NOCASE", (searchword,))

        data = cur.fetchone()
        if data is None:
            return 'notFound'
        else:
            return data[0]

def database_read_rows(db):
    allrows = []
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        for idx, row in enumerate(cur.execute("SELECT * FROM URLS")):
            newrow = list(row) + [idx+1]
            allrows.append(newrow)
    return allrows

def set_as_collected(db, rowid):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute("""UPDATE URLS SET IsCollected=? WHERE ROWID = ?""", ('x', rowid))

def parse_rows(row):
    title = row[0]
    url = row[1]
    description = row[2]
    pubdate = row[3]
    permlink = row[4]
    image = row[5]
    catlist = row[6:15]
    catlist = [x for x in catlist if x != '']
    creator = row[15]
    rights = row[16]
    rssfeed = row[17]
    iscollected = row[18]
    rowidx = row[19]
    return title, url, description, pubdate, permlink, image, catlist, creator, rights, rssfeed, iscollected, rowidx

'''
with open(os.getcwd() + '/geonames-be.ner', 'r', encoding='utf-8') as f:
    cities = f.readlines()
cities = [re.sub(r'\n', '', x) for x in cities]
currentpath = os.getcwd()
for city in cities:
    database_main(currentpath + '/geonames-be.db', [city])
'''