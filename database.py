import sqlite3


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self.user_id = None

    def create_table(self, user_id):
        self.user_id = user_id
        self.cursor.execute("CREATE TABLE IF NOT EXISTS `%s`(word_id INT, english_word TEXT, translation TEXT)"
                            % (user_id))

    def inserting(self, word_num, word, translation):
        try:
            self.cursor.execute("INSERT INTO `%s`(word_id, english_word, translation) VALUES(?, ?, ?)"
                                % (self.user_id), (word_num, word, translation))
            self.conn.commit()
        except Exception as e:
            print(e)

    def close(self):
        self.cursor.close()
        self.conn.close()
