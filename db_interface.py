import mariadb

class DB_Interface():
    def __init__(self):
        self.db_connection = mariadb.connect(
            user="dascrapy_user",
            password="dascrapy_user",
            host="127.0.0.1",
            port=3306,
            database="dascrapy")
        self.session = self.db_connection.cursor()

    def check_url(self, url):
        print("Checking url: %s" % url)
        
        self.session.execute(f"select id from urls where urls.data like '{url}' limit 1;")

        is_there = self.session.fetchone()

        if not is_there:
            return False
        else:
            return True
        
    def proc(self, username, url, date, urlType, gl_inc):
        if self.check_url(url) == True:
            print(f"Checking Received url: {url}")
            print("Url found in database. Not inserting.")
            return

        self.session.execute(f"select id from deviants where username like '{username}' limit 1;")

        deviant_id = self.session.fetchone()
        if not deviant_id:
            print("inserting username: %s" % username)
            self.session.execute("insert into deviants (username) values ('%s')" % username)

            self.db_connection.commit()
            deviant_id = self.session.lastrowid
            print("Deviant Id of last insert: %s" % deviant_id)
        else:
            print("Deviant Id Found: %s" % deviant_id)
            deviant_id = deviant_id[0]

        if date == False:
            date = "NULL"

        self.session.execute(f"insert into urls (data, urlType, urlDate, global_inc, deviant_id) values ('{url}', '{urlType}', '{date}', {gl_inc}, {deviant_id})")
        self.db_connection.commit()
