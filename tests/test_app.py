# --------------------------------------------------
#Flask Test Cases
# --------------------------------------------------

import os
import sqlite3
import re

import pytest
from app import app


# --------------------------------------------------
# TEST DATABASE
# --------------------------------------------------

@pytest.fixture
def test_database(tmp_path):
    """
    Create a temporary SQLite database for testing.
    It is automatically deleted after each test.
    """

    db_path = tmp_path / "test_database.db"

    conn = sqlite3.connect(db_path)

    conn.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            author_url TEXT,
            rating INTEGER NOT NULL,
            review TEXT NOT NULL,
            date TEXT NOT NULL,
            cover_url TEXT
        )
    """)

    conn.execute("""
        INSERT INTO reviews
        (title, author, author_url, rating, review, date, cover_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Test Book",
        "Test Author",
        "https://example.com",
        5,
        "This is a test review.",
        "2026-08-13",
        "https://example.com/cover.jpg"
    ))

    conn.commit()
    conn.close()

    return str(db_path)


# --------------------------------------------------
# TEST CLIENT
# --------------------------------------------------

@pytest.fixture
def client(test_database):
    """
    Create a Flask test client using the temporary database.
    """

    app.config["TESTING"] = True
    app.config["DATABASE"] = test_database
    app.config["SECRET_KEY"] = "test-secret-key"

    # Enable CSRF during tests if your app uses Flask-WTF
    app.config["WTF_CSRF_ENABLED"] = True

    os.environ["ADMIN_PASSWORD"] = "test-password"

    with app.test_client() as client:
        yield client


# --------------------------------------------------
# CSRF HELPER
# --------------------------------------------------

def get_csrf_token(client):
    """
    Get the CSRF token from the login page.
    """

    response = client.get("/login")

    assert response.status_code == 200

    match = re.search(
        rb'name="csrf_token" value="([^"]+)"',
        response.data
    )

    assert match is not None

    return match.group(1).decode()


# --------------------------------------------------
# LOGIN HELPER
# --------------------------------------------------

def login(client):
    """
    Log into the admin account.
    """

    token = get_csrf_token(client)

    return client.post(
        "/login",
        data={
            "password": "test-password",
            "csrf_token": token
        },
        follow_redirects=True
    )


# --------------------------------------------------
# PUBLIC PAGES
# --------------------------------------------------

def test_home_page(client):

    response = client.get("/")

    assert response.status_code == 200


def test_books_page(client):

    response = client.get("/books")

    assert response.status_code == 200
    assert b"Test Book" in response.data


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def test_admin_requires_login(client):

    response = client.get("/admin")

    assert response.status_code == 302
    assert "/login" in response.location


def test_login_page_loads(client):

    response = client.get("/login")

    assert response.status_code == 200


def test_wrong_password(client):

    token = get_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "password": "wrong-password",
            "csrf_token": token
        }
    )

    assert response.status_code == 200
    assert b"Incorrect password" in response.data


def test_correct_password(client):

    response = login(client)

    assert response.status_code == 200
    assert b"Test Book" in response.data


def test_empty_password(client):

    token = get_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "password": "",
            "csrf_token": token
        }
    )

    assert response.status_code == 200
    assert b"Incorrect password" in response.data


def test_similar_but_wrong_password(client):

    token = get_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "password": "test-passwor",
            "csrf_token": token
        }
    )

    assert response.status_code == 200
    assert b"Incorrect password" in response.data


def test_password_is_case_sensitive(client):

    token = get_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "password": "TEST-PASSWORD",
            "csrf_token": token
        }
    )

    assert response.status_code == 200
    assert b"Incorrect password" in response.data


def test_successful_login_allows_admin_access(client):

    token = get_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "password": "test-password",
            "csrf_token": token
        }
    )

    assert response.status_code == 302

    response = client.get("/admin")

    assert response.status_code == 200


# --------------------------------------------------
# ADMIN
# --------------------------------------------------

def test_admin_page(client):

    login(client)

    response = client.get("/admin")

    assert response.status_code == 200
    assert b"Test Book" in response.data


def test_add_book_requires_login(client):

    response = client.get("/admin/add-book")

    assert response.status_code == 302
    assert "/login" in response.location


def test_edit_book_requires_login(client):

    response = client.get("/admin/edit-book/1")

    assert response.status_code == 302
    assert "/login" in response.location


# --------------------------------------------------
# ADD BOOK
# --------------------------------------------------

def test_add_book(client, test_database):

    login(client)

    token = get_csrf_token(client)

    response = client.post(
        "/admin/add-book",
        data={
            "title": "New Test Book",
            "author": "New Test Author",
            "author_url": "https://example.com/author",
            "rating": "4",
            "review": "A new test review.",
            "date": "2026-08-14",
            "cover_url": "https://example.com/new-cover.jpg",
            "csrf_token": token
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"New Test Book" in response.data

    conn = sqlite3.connect(test_database)

    book = conn.execute(
        "SELECT * FROM reviews WHERE title = ?",
        ("New Test Book",)
    ).fetchone()

    conn.close()

    assert book is not None

    # Database columns:
    # 0 = id
    # 1 = title
    # 2 = author
    # 3 = author_url
    # 4 = rating
    # 5 = review
    # 6 = date
    # 7 = cover_url

    assert book[2] == "New Test Author"
    assert book[5] == "A new test review."


# --------------------------------------------------
# EDIT BOOK
# --------------------------------------------------

def test_edit_book_page(client):

    login(client)

    response = client.get("/admin/edit-book/1")

    assert response.status_code == 200
    assert b"Test Book" in response.data


def test_edit_book(client, test_database):

    login(client)

    token = get_csrf_token(client)

    response = client.post(
        "/admin/edit-book/1",
        data={
            "title": "Updated Test Book",
            "author": "Updated Author",
            "author_url": "https://example.com/updated",
            "rating": "3",
            "review": "Updated review.",
            "date": "2026-08-15",
            "cover_url": "https://example.com/updated.jpg",
            "csrf_token": token
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Updated Test Book" in response.data

    conn = sqlite3.connect(test_database)

    book = conn.execute(
        "SELECT * FROM reviews WHERE id = 1"
    ).fetchone()

    conn.close()

    assert book is not None

    assert book[1] == "Updated Test Book"
    assert book[2] == "Updated Author"
    assert book[5] == "Updated review."


# --------------------------------------------------
# INVALID BOOK
# --------------------------------------------------

def test_edit_nonexistent_book(client):

    login(client)

    response = client.get("/admin/edit-book/9999")

    assert response.status_code == 404


# --------------------------------------------------
# DELETE BOOK
# --------------------------------------------------

def test_delete_book_requires_login(client):

    token = get_csrf_token(client)

    response = client.post(
        "/admin/delete-book/1",
        data={
            "csrf_token": token
        }
    )

    assert response.status_code == 302
    assert "/login" in response.location


def test_delete_book(client, test_database):

    login(client)

    token = get_csrf_token(client)

    response = client.post(
        "/admin/delete-book/1",
        data={
            "csrf_token": token
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Book deleted successfully!" in response.data

    conn = sqlite3.connect(test_database)

    book = conn.execute(
        "SELECT * FROM reviews WHERE id = 1"
    ).fetchone()

    conn.close()

    assert book is None


def test_delete_nonexistent_book(client):

    login(client)

    token = get_csrf_token(client)

    response = client.post(
        "/admin/delete-book/9999",
        data={
            "csrf_token": token
        }
    )

    assert response.status_code == 404


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

def test_logout(client):

    login(client)

    response = client.get(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200

    response = client.get("/admin")

    assert response.status_code == 302
    assert "/login" in response.location