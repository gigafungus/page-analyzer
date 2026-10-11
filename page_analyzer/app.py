import os
from urllib.parse import urlparse

import psycopg
from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, url_for
from validators import url

from page_analyzer.url_repo import Urls

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
DATABASE_URL = os.environ["DATABASE_URL"]
app.logger.setLevel("DEBUG")

@app.before_request
def open_connection():
    g.conn = psycopg.connect(DATABASE_URL)
    g.repo = Urls(g.conn)

@app.teardown_request
def clear_connection(exception=None):
    conn: psycopg.Connection = g.pop("conn", None)
    if conn is not None:
        conn.close()

@app.route('/')
def main_page():
    return render_template('title.html')

@app.post('/urls')
def add_url():
    form_data = request.form.get('url')
    if form_data is None or len(form_data) > 255 or url(form_data) is not True:
        flash('Адрес недействителен', 'error')
        return render_template('title.html'), 422
    splitted = urlparse(form_data)
    normalized = f"{splitted.scheme}://{splitted.hostname}"
    record = g.repo.find(url=normalized)
    if not record:
        id = g.repo.save_url(normalized)
        flash('Страница успешно добавлена', 'success')
    else:
        id = record['id']
        flash('Страница уже существует', 'message')
    return redirect(url_for('show_one', id=id))


@app.get('/urls/<int:id>')
def show_one(id):
    record = g.repo.find(id=id)
    if not record:
        flash('Адрес не найден', 'error')
        return render_template('title.html'), 404
    url_checks = g.repo.list_checks(id)
    return render_template('show_one.html', url=record, checks=url_checks)

@app.get('/urls')
def show_all():
    catalog = g.repo.catalog()
    return render_template('show_all.html', records=catalog)
    
@app.post('/urls/<int:id>/checks')
def check_url(id):
    checked = g.repo.save_check(id)
    if checked:
        flash('Страница успешно проверена', 'success')
    else:
        flash('Произошла ошибка при проверке', 'error')
    return redirect(url_for('show_one', id=id))
       

