# Created on 2018-07-04
# Author: Binbin Zhang

import MySQLdb

CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'passwd': 'admin',
    'db': 'kws',
    'charset': 'utf8'
}

class DbHelper:
    def __init__(self, **kvargs):
        self.connection = MySQLdb.connect(**kvargs)
        self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    def table_exist(self):
        sql_cmd = '''SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'review' '''
        self.cursor.execute(sql_cmd)
        if self.cursor.fetchone()[0] == 0:
            return False
        else:
            return True

    def create_table(self):
        sql_cmd = '''CREATE TABLE review
                     (id int NOT NULL AUTO_INCREMENT,
                      wav_path text NOT NULL,
                      valid boolean NOT NULL,
                      status boolean NOT NULL,
                      PRIMARY KEY (id) ) CHARSET=utf8'''
        self.cursor.execute(sql_cmd)

    def insert(self, wav_path, valid, status):
        sql_cmd = '''INSERT INTO review (wav_path, valid, status)
                     VALUES ("%s", %s, %s) ''' % (wav_path, valid, status)
        try:
            self.cursor.execute(sql_cmd)
            self.connection.commit()
        except MySQLdb.Error as e:
            self.connection.rollback()

    def update(self, id, valid, status):
        sql_cmd = '''UPDATE review SET valid=%s, status=%s
                     WHERE id=%d''' % (valid, status, id)
        try:
            self.cursor.execute(sql_cmd)
            self.connection.commit()
        except MySQLdb.Error as e:
            self.connection.rollback()

    def get_review_count(self):
        sql_cmd = '''SELECT COUNT(*) FROM review'''
        self.cursor.execute(sql_cmd)
        return self.cursor.fetchone()[0]

    def get_all_review(self, offset, number):
        sql_cmd = '''SELECT * FROM review ORDER BY id ASC LIMIT %d,%d''' % (offset, number)
        self.cursor.execute(sql_cmd)
        return self.cursor.fetchall()

if __name__ == '__main__':
    print(CONFIG)
    db = DbHelper(**CONFIG)
    if not db.table_exist():
        db.create_table()
    db.insert('a.wav', 'true', 'true')
    db.insert('b.wav', 'true', 'false')
    print(db.get_all_review())

