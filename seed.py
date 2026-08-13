import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

reviews = [
    (
        'Remarkably Bright Creatures',
        'Shelby Van Pelt',
        'https://www.goodreads.com/author/show/21374195.Shelby_Van_Pelt',
        5,
        '''Okay so where to start. This is an incredibly wholesome book, once I picked it up I legit could not stop.
Marcellus is mischievous but a great little detective hehe. I loved all aspects of this book and I was
so intrigued as to how it would all come together. Shelby Van Pelt better write more books because
this was such a hit.''',
        '2026-03-12',
        'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1651600548l/58733693._SX98_.jpg'
    ),

    (
        'Red Rising',
        'Pierce Brown',
        'https://www.goodreads.com/author/show/6474348.Pierce_Brown',
        5,
        '''Omg this is such a good story, absolutely love Darrow as a character. I would a million percent
recommend to anyone and everyone who enjoys Dystopian/Fantasy genres to read this book ASAP. It is
such a good depiction of the current real-world hierarchical structure and how our 'golds' (Rich
folk) treat the rest of us 'low Colours'. Cannot wait to read the next one I'm starting it tomorrow.''',
        '2026-07-15',
        'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1461354651l/15839976._SX98_.jpg'
    ),

    (
        'Golden Son',
        'Pierce Brown',
        'https://www.goodreads.com/author/show/6474348.Pierce_Brown',
        5,
        'Still reading this one, so far so good though.',
        '2026-08-13',
        'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1394684475l/18966819._SX98_.jpg'
    )
]

cursor.executemany('''
INSERT INTO reviews
(title, author, author_url, rating, review, date, cover_url)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', reviews)

conn.commit()
conn.close()

print('Reviews added successfully!')