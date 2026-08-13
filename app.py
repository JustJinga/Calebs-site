from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required
)
import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


app.secret_key = os.environ['FLASK_SECRET_KEY']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Admin(UserMixin):
    id = 'admin'


@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return Admin()

    return None


# Database helper

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Public pages

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/books')
def book_reviews():

    conn = get_db()

    reviews = conn.execute(
        'SELECT * FROM reviews ORDER BY date DESC'
    ).fetchall()

    conn.close()

    return render_template(
        'book_reviews.html',
        reviews=reviews
    )


# Login

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        password = request.form.get('password')
        admin_password = os.environ.get('ADMIN_PASSWORD')

        if admin_password and password == admin_password:

            login_user(Admin())

            return redirect(url_for('admin'))

        flash('Incorrect password.')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('home'))


# Admin homepage

@app.route('/admin')
@login_required
def admin():

    conn = get_db()

    reviews = conn.execute(
        'SELECT * FROM reviews ORDER BY date DESC'
    ).fetchall()

    conn.close()

    return render_template(
        'admin.html',
        reviews=reviews
    )

# Add book

@app.route('/admin/add-book', methods=['GET', 'POST'])
@login_required
def add_book():

    if request.method == 'POST':

        title = request.form.get('title')
        author = request.form.get('author')
        author_url = request.form.get('author_url')
        rating = request.form.get('rating')
        review = request.form.get('review')
        date = request.form.get('date')
        cover_url = request.form.get('cover_url')

        conn = get_db()

        conn.execute(
            '''
            INSERT INTO reviews
            (title, author, author_url, rating, review, date, cover_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                title,
                author,
                author_url,
                rating,
                review,
                date,
                cover_url
            )
        )

        conn.commit()
        conn.close()

        flash('Book added successfully!')

        return redirect(url_for('admin'))

    return render_template('add_book.html')


# Edit book

@app.route('/admin/edit-book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):

    conn = get_db()

    book = conn.execute(
        'SELECT * FROM reviews WHERE id = ?',
        (book_id,)
    ).fetchone()

    if book is None:

        conn.close()

        return 'Book not found', 404


    if request.method == 'POST':

        title = request.form.get('title')
        author = request.form.get('author')
        author_url = request.form.get('author_url')
        rating = request.form.get('rating')
        review = request.form.get('review')
        date = request.form.get('date')
        cover_url = request.form.get('cover_url')

        conn.execute(
            '''
            UPDATE reviews
            SET
                title = ?,
                author = ?,
                author_url = ?,
                rating = ?,
                review = ?,
                date = ?,
                cover_url = ?
            WHERE id = ?
            ''',
            (
                title,
                author,
                author_url,
                rating,
                review,
                date,
                cover_url,
                book_id
            )
        )

        conn.commit()
        conn.close()

        flash('Book updated successfully!')

        return redirect(url_for('admin'))


    conn.close()

    return render_template(
        'edit_book.html',
        book=book
    )


if __name__ == '__main__':
    app.run(port=8080, debug=True)