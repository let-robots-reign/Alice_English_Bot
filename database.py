import psycopg2
import urllib.parse as urlparse
import os

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port


class DataBase:
    def __init__(self):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()
        self.user_id = None

    def create_table(self, user_id):
        self.user_id = user_id
        self.cursor.execute("CREATE TABLE IF NOT EXISTS `{}` (word_id integer, english_word varchar, translation varchar, "
                            "completion integer)".format(user_id))

    def insert_word(self, word_num, word, translation):
        try:
            self.cursor.execute("INSERT INTO `{}` (word_id, english_word, translation, completion) "
                                "VALUES(%s, %s, %s, %s)".format(self.user_id), (word_num, word, translation, 0))
            self.conn.commit()
        except Exception as e:
            print(e)

    def increment_completion(self, word):
        self.cursor.execute("SELECT completion FROM `{}` "
                            "WHERE english_word = %s;".format(self.user_id), (word,))
        current_completion = self.cursor.fetchall()
        self.cursor.execute("UPDATE `{}` SET completion = %s WHERE english_word = %s;".format(self.user_id),
                            (str(int(current_completion[0][0]) + 25), word))
        self.conn.commit()

    def select_uncompleted_words(self):
        self.cursor.execute("SELECT english_word, translation FROM `{}` WHERE completion < 100;".format(self.user_id))
        return self.cursor.fetchall()

    def read_dict(self):
        self.cursor.execute("SELECT * FROM `{}`".format(self.user_id))
        return self.cursor.fetchall()

    def delete_dict(self):
        self.cursor.execute("DELETE FROM `{}`".format(self.user_id))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
