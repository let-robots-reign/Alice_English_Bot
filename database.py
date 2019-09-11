import sqlite3


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self.user_id = None

    def create_table(self, user_id):
        self.user_id = user_id
        self.cursor.execute("CREATE TABLE IF NOT EXISTS `%s`(word_id INT, english_word TEXT, translation TEXT, "
                            "completion INT)" % (user_id))

    def insert_word(self, word_num, word, translation):
        try:
            self.cursor.execute("INSERT INTO `%s`(word_id, english_word, translation, completion) VALUES(?, ?, ?, ?)"
                                % (self.user_id), (word_num, word, translation, 0))
            self.conn.commit()
        except Exception as e:
            print(e)

    def increment_completion(self, word):
        self.cursor.execute("SELECT completion FROM `%s` "
                            "WHERE english_word = ?;" % (self.user_id), (word,))
        current_completion = self.cursor.fetchall()
        self.cursor.execute("UPDATE `%s` SET completion = ? WHERE english_word = ?;" % (self.user_id),
                            (str(int(current_completion[0][0]) + 25), word))
        self.conn.commit()

    def select_uncompleted_words(self):
        self.cursor.execute("SELECT english_word, translation FROM `%s` WHERE completion < 100;" % (self.user_id))
        return self.cursor.fetchall()

    def read_dict(self):
        self.cursor.execute("SELECT * FROM `%s`" % (self.user_id))
        return self.cursor.fetchall()

    def delete_dict(self):
        self.cursor.execute("DELETE FROM `%s`" % (self.user_id))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
