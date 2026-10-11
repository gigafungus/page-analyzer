import datetime as dt

import psycopg
from psycopg.rows import DictRow, dict_row


class Urls:
    def __init__(self, connection):
        self.conn: psycopg.Connection = connection

    def save_url(self, url):
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
            cur.execute('''WITH max_for_url AS (SELECT MAX(id), url_id FROM url_checks GROUP BY url_id),
                        last_checks AS (SELECT * FROM url_checks WHERE id in (SELECT max FROM max_for_url))
                        SELECT u.id, u.name, lc.status_code, lc.created_at as last_check FROM urls AS u 
                        LEFT JOIN last_checks AS lc ON u.id = lc.url_id ORDER BY u.id DESC''')
            result = cur.fetchall()
            return result

    def save_check(self, id):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO url_checks (url_id, created_at) VALUES (%s, %s) RETURNING id", 
                        (id, dt.datetime.now(tz=dt.UTC).date()))
            check_id = cur.fetchone()[0] # type: ignore
        self.conn.commit()
        return check_id

    def list_checks(self, id) -> list[DictRow]:
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM url_checks WHERE url_id=%s ORDER BY id DESC", (id,))
            result = cur.fetchall()
            return result


        

