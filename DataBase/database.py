import sqlite3

db = sqlite3.connect( "DataBase/bot.db" )
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users( id INTEGER, age TEXT, gender TEXT, param TEXT, dataTrain TEXT )")
cur.execute("CREATE TABLE IF NOT EXISTS dicts( id INTEGER, name TEXT, content TEXT )")
db.commit()

class DataBase:
    def __init__( self, name: str ) -> None:
        self.name = name

    async def create( self, page_id: str ) -> None:
        page = cur.execute( f"""SELECT * FROM { self.name } WHERE id == ?""", (page_id, ) ).fetchone()
        if not page:
            cur.execute( f"""INSERT INTO { self.name } (id) VALUES (?)""", (page_id, ) )
            db.commit()

    async def remove( self, page_id: int ) -> None:
        page = cur.execute ( f"""SELECT * FROM { self.name } WHERE id = ?""", (page_id, ) ).fetchone()
        if page:
            page = cur.execute( f"""DELETE FROM { self.name } WHERE id = ?""", (page_id, ) ).fetchone()
            db.commit()

    async def enter( self, page_id: int, name: str, content: str ) -> None:
        page = cur.execute( f"""SELECT * FROM { self.name } WHERE id == ?""", (page_id, ) ).fetchone()
        if page:
            cur.execute( f"""UPDATE { self.name } SET { name } = ? WHERE id = ?""", (content, page_id, ) )
            db.commit()

    async def get( self, page_id: int, name: str ) -> list:
        page = cur.execute( f"""SELECT * FROM { self.name } WHERE id == ?""", (page_id, ) ).fetchone()
        result = ""
        if self.name == 'users':
            names = { 'id': 0, 'age': 1, 'gender': 2, 'param': 3, 'dataTrain': 4 }
        elif self.name == 'dicts':
            names = { 'id': 0, 'name': 1, 'content': 2 }
        if page[names[name]]:
            result = page[names[name]]
        return result
        
    async def get_all( self ) -> list:
        pages = cur.execute( f"""SELECT * FROM { self.name }""" ).fetchall()
        return pages
        
    async def get_count_not_empty_in_page( self, page_id: int ) -> list:
        page = cur.execute( f"""SELECT * FROM { self.name } WHERE id == ?""", (page_id, ) ).fetchone()
        if page:
            return len(page) - page.count(None)
        return 0

users_db = DataBase("users")
dicts_db = DataBase("dicts")
