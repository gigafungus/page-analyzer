import datetime as dt

import psycopg
from psycopg.rows import DictRow, dict_row


class Urls:
    def __init__(self, connection):
        self.conn: psycopg.Connection = connection

    def save(self, url):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id", 
                        (url, dt.datetime.now(tz=dt.UTC).date()))
            id = cur.fetchone()[0] # type: ignore
        self.conn.commit()
        return id

    def find(self, id=None, url=None) -> DictRow | None:
        with self.conn.cursor(row_factory=dict_row) as cur:
            if url:
                cur.execute("SELECT * FROM urls WHERE name=%s", (url,))
            elif id and id > 0:
                cur.execute("SELECT * FROM urls WHERE id=%s", (id,))
            else:
                return None
            data = cur.fetchone()
            return data

    def catalog(self) -> list[DictRow]:
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM urls ORDER BY id DESC")
            result = cur.fetchall()
            return result
        

