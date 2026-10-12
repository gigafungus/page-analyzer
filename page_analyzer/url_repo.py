import datetime as dt

import psycopg
from psycopg.rows import DictRow, dict_row


class Urls:
    def __init__(self, connection: psycopg.Connection):
        self.conn = connection

    def save_url(self, url: str):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id", 
                        (url, dt.datetime.now(tz=dt.UTC).date()))
            id = cur.fetchone()[0] # type: ignore
        self.conn.commit()
        return id

    def find(self, id: int|None = None, url: str|None = None) -> DictRow | None:
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
            cur.execute('''WITH max_for_url AS (SELECT MAX(id), url_id FROM url_checks GROUP BY url_id),
                        last_checks AS (SELECT * FROM url_checks WHERE id in (SELECT max FROM max_for_url))
                        SELECT u.id, u.name, lc.status_code, lc.created_at as last_check FROM urls AS u 
                        LEFT JOIN last_checks AS lc ON u.id = lc.url_id ORDER BY u.id DESC''')
            result = cur.fetchall()
            return result

    def save_check(self, data: dict):
        with self.conn.cursor() as cur:
            cur.execute('''INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)''',
                            (data['url_id'], data['status_code'],data.get('h1'), data.get('title'),
                            data.get('description'), dt.datetime.now(tz=dt.UTC).date()))
        self.conn.commit()

    def list_checks(self, id: int) -> list[DictRow]:
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM url_checks WHERE url_id=%s ORDER BY id DESC", (id,))
            result = cur.fetchall()
            return result


        

