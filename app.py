from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = 'elite.db'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'change-this-secret-key')


def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_name TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER NOT NULL,
            branch_name TEXT NOT NULL,
            FOREIGN KEY (program_id) REFERENCES programs(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            student_id TEXT NOT NULL,
            dob TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            program_id INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            year_of_study TEXT NOT NULL,
            FOREIGN KEY (program_id) REFERENCES programs(id),
            FOREIGN KEY (branch_id) REFERENCES branches(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS parents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            parent_type TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            program_id INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            FOREIGN KEY (program_id) REFERENCES programs(id),
            FOREIGN KEY (branch_id) REFERENCES branches(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            image_url TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            program_id INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            enrollment_year INTEGER NOT NULL,
            FOREIGN KEY (program_id) REFERENCES programs(id),
            FOREIGN KEY (branch_id) REFERENCES branches(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            faculty_username TEXT,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(student_id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS faculty_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            faculty_username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(student_id),
            FOREIGN KEY (faculty_username) REFERENCES faculty(username)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            FOREIGN KEY (branch_id) REFERENCES branches(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS student_id_sequences (
            program_id INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            last_number INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (program_id, branch_id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS student_number_counter (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_number INTEGER NOT NULL DEFAULT 99
        )
    ''')

    faculty_columns = {row[1] for row in c.execute('PRAGMA table_info(faculty)').fetchall()}
    if 'subject_id' not in faculty_columns:
        c.execute('ALTER TABLE faculty ADD COLUMN subject_id INTEGER')
    if 'teaching_year' not in faculty_columns:
        c.execute('ALTER TABLE faculty ADD COLUMN teaching_year INTEGER')

    conn.commit()

    if c.execute('SELECT COUNT(*) FROM programs').fetchone()[0] == 0:
        programs = ["Engineering", "Business Administration", "Health Sciences", "Environmental Studies", "Fine Arts"]
        c.executemany('INSERT INTO programs (program_name) VALUES (?)', [(p,) for p in programs])

    if c.execute('SELECT COUNT(*) FROM branches').fetchone()[0] == 0:
        branch_map = {
            "Engineering": ["Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Computer Science", "Chemical Engineering"],
            "Business Administration": ["Finance", "Marketing", "Human Resources", "Operations Management", "International Business"],
            "Health Sciences": ["Nursing", "Pharmacy", "Public Health", "Physiotherapy", "Biomedical Science"],
            "Environmental Studies": ["Environmental Science", "Environmental Policy", "Sustainable Development", "Conservation Biology", "Climate Science"],
            "Fine Arts": ["Visual Arts", "Performing Arts", "Music", "Dance", "Theatre"]
        }
        for program_name, branches in branch_map.items():
            program_id = c.execute('SELECT id FROM programs WHERE program_name = ?', (program_name,)).fetchone()[0]
            c.executemany('INSERT INTO branches (program_id, branch_name) VALUES (?, ?)', [(program_id, branch) for branch in branches])

    if c.execute('SELECT COUNT(*) FROM subjects').fetchone()[0] == 0:
        subject_rows = [
            (4, 1, 'Data Structures'), (4, 1, 'Computer Organization'), (4, 1, 'Discrete Mathematics'),
            (4, 2, 'Algorithms'), (4, 2, 'Operating Systems'), (4, 2, 'Database Management Systems'),
            (4, 3, 'Theory of Computation'), (4, 3, 'Computer Networks'),
            (2, 1, 'Introduction to Business'), (2, 1, 'Principles of Management'), (2, 1, 'Accounting Basics'),
            (2, 2, 'Marketing Principles'), (2, 2, 'Financial Management'), (2, 2, 'Business Law'),
            (2, 3, 'Strategic Management'), (2, 3, 'Human Resource Management'), (2, 3, 'Operations Management'),
            (2, 4, 'International Business'), (2, 4, 'Entrepreneurship'), (2, 4, 'Business Ethics'),
            (3, 1, 'Human Anatomy'), (3, 1, 'Introduction to Health Science'), (3, 1, 'Public Health Basics'),
            (3, 2, 'Medical Terminology'), (3, 2, 'Health Policy'), (3, 2, 'Epidemiology'),
            (3, 3, 'Clinical Practice'), (3, 3, 'Health Education'), (3, 3, 'Research Methods in Health Science'),
            (3, 4, 'Healthcare Management'), (3, 4, 'Advanced Clinical Skills'), (3, 4, 'Health Promotion'),
            (4, 1, 'Environmental Science'), (4, 1, 'Ecology'), (4, 1, 'Environmental Policy'),
            (4, 2, 'Climate Change'), (4, 2, 'Conservation Biology'), (4, 2, 'Environmental Impact Assessment'),
            (4, 3, 'Sustainable Development'), (4, 3, 'Environmental Law'), (4, 3, 'Resource Management'),
            (4, 4, 'Environmental Health'), (4, 4, 'Global Environmental Issues'), (4, 4, 'Capstone Project'),
            (5, 1, 'Art History'), (5, 1, 'Drawing Fundamentals'), (5, 1, 'Visual Arts Practice'),
            (5, 2, 'Sculpture'), (5, 2, 'Painting Techniques'), (5, 2, 'Art Theory'),
            (5, 3, 'Printmaking'), (5, 3, 'Digital Art'), (5, 3, 'Advanced Studio Practice'),
            (5, 4, 'Art Criticism'), (5, 4, 'Professional Practices'), (5, 4, 'Final Exhibition')
        ]
        c.executemany('INSERT INTO subjects (branch_id, year, subject_name) VALUES (?, ?, ?)', subject_rows)

    if c.execute('SELECT COUNT(*) FROM events').fetchone()[0] == 0:
        sample_events = [
            ('New Year Celebration', 'Celebrate the start of the new year.', '2024-01-01', '12:00 AM - 12:00 AM', 'new_year.jpg'),
            ('Republic Day Celebration', 'Celebrate Republic Day with a flag hoisting ceremony.', '2024-01-26', '8:00 AM - 10:00 AM', 'republic_day.jpg'),
            ('Makarsankranti / Pongal', 'Celebrate the harvest festival.', '2024-01-14', '10:00 AM - 1:00 PM', 'makarsankranti.jpg'),
            ('Parent-Teacher Conference', 'Discuss your child’s progress.', '2024-03-15', '4:00 PM - 6:00 PM', 'parent_teacher.jpg'),
            ('Holi Festival', 'Celebrate the vibrant festival of Holi.', '2024-03-25', '11:00 AM - 2:00 PM', 'holi.jpg'),
            ('Ugadi / Gudi Padwa / Telugu New Year', 'Celebrate the new year according to the Hindu calendar.', '2024-03-30', '10:00 AM - 1:00 PM', 'ugadi.jpg'),
            ('Eid al-Fitr Celebration', 'Celebrate the end of Ramadan.', '2024-04-10', '12:00 PM - 2:00 PM', 'Ramadan.jpg'),
            ('Spring Concert', 'Enjoy performances by the school choir and band.', '2024-04-10', '7:00 PM - 9:00 PM', 'spring_concert.jpg'),
            ('Science Fair', 'View student science projects.', '2024-05-20', '9:00 AM - 12:00 PM', 'science_fair.jpg'),
            ('Ethnic Day', 'Showcase traditional attire from different cultures.', '2024-05-25', '10:00 AM - 1:00 PM', 'ethnic_day.jpg'),
            ('Sports Day', 'Join us for a day of fun and games.', '2024-06-15', '10:00 AM - 3:00 PM', 'sports_day.jpg'),
            ('Eid al-Adha Event', 'Celebrate Eid al-Adha with traditional meals.', '2024-06-17', '1:00 PM - 3:00 PM', 'eid.jpg'),
            ('Independence Day Celebration', 'Celebrate Independence Day with a flag hoisting ceremony.', '2024-08-15', '8:00 AM - 10:00 AM', 'independence_day.jpg'),
            ('Ganesh Chaturthi', 'Celebrate the festival of Ganesh Chaturthi.', '2024-08-22', '10:00 AM - 1:00 PM', 'ganesh_chaturthi.jpg'),
            ('Farewell Party', 'Bid farewell to the graduating students.', '2024-09-05', '5:00 PM - 8:00 PM', 'farewell.jpg'),
            ('Voting Day', 'Participate in the school elections.', '2024-10-10', '9:00 AM - 5:00 PM', 'voting_day.jpg'),
            ('Movie Day', 'Enjoy a movie screening at the school.', '2024-10-20', '3:00 PM - 6:00 PM', 'movie_day.jpg'),
            ('Dusshera', 'Celebrate the victory of good over evil.', '2024-10-24', '10:00 AM - 1:00 PM', 'dusshera.jpg'),
            ('Halloween Parade', 'Students can dress up in costumes.', '2024-10-31', '1:00 PM - 3:00 PM', 'halloween_parade.jpg'),
            ('Diwali', 'Celebrate the festival of lights.', '2024-11-12', '5:00 PM - 9:00 PM', 'diwali.jpg'),
            ('Graduation Party', 'Celebrate the achievements of the graduates.', '2024-12-10', '6:00 PM - 9:00 PM', 'graduation.jpg'),
            ('Christmas Celebration', 'Join our Christmas celebration.', '2024-12-15', '5:00 PM - 8:00 PM', 'christmas.jpg'),
            ('Winter Concert', 'Enjoy holiday music performances.', '2024-12-15', '7:00 PM - 9:00 PM', 'winter_concert.jpg')
        ]
        c.executemany('INSERT INTO events (title, description, date, time, image_url) VALUES (?, ?, ?, ?, ?)', sample_events)

    conn.commit()
    conn.close()


# Function to query the database
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def generate_student_id(conn, program_id, branch_id):
    """Allocate a permanent numeric three-digit student ID."""
    conn.execute(
        'INSERT OR IGNORE INTO student_number_counter (id, last_number) VALUES (1, 99)'
    )
    conn.execute(
        'UPDATE student_number_counter SET last_number = last_number + 1 WHERE id = 1'
    )
    sequence = conn.execute(
        'SELECT last_number FROM student_number_counter WHERE id = 1'
    ).fetchone()[0]
    if sequence > 999:
        raise ValueError('The three-digit student ID range is full.')
    return f'{sequence:03d}'

# Function to add a user to the database
def add_user(username, password, student_id, dob, email, phone, address, program_id, branch_id, year_of_study):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO users(username, password, student_id, dob, email, phone, address, program_id, branch_id, year_of_study) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (username, password, student_id, dob, email, phone, address, program_id, branch_id, year_of_study))
    conn.commit()
    conn.close()

initialize_database()

def parent_user(username, password,  email, phone, student_id, student_name, parent_type):
    conn = sqlite3.connect('elite.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO parents(username, password,  email, phone, student_id, student_name, parent_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, password,  email, phone, student_id, student_name, parent_type))
    conn.commit()
    conn.close()

#function to add a faculty
def add_faculty(username, password, email, phone, program_id, branch_id):
    conn = sqlite3.connect('elite.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO faculty (username, password, email, phone, program_id, branch_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password, email, phone, program_id, branch_id))
    conn.commit()
    conn.close()

def add_program(program):
    conn = sqlite3.connect('elite.db')
    c = conn.cursor()
    c.execute('INSERT INTO programs (program_name) VALUES (?)', (program,))
    conn.commit()
    conn.close()

def add_branch(program_id, branch):
    conn = sqlite3.connect('elite.db')
    c = conn.cursor()
    c.execute('INSERT INTO branches (program_id, branch_name) VALUES (?, ?)', (program_id, branch))
    conn.commit()
    conn.close()

# Function to add events
def add_event(title, description, date, time, image_url):
    try:
        conn = sqlite3.connect('elite.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO events (title, description, date, time, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, date, time, image_url))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding event: {e}")
    finally:
        conn.close()

def add_subject(subject_name, branch_id, year):
    conn = sqlite3.connect('elite.db')
    c = conn.cursor()
    c.execute('INSERT INTO subjects (subject_name, branch_id, year) VALUES (?, ?, ?)', (subject_name, branch_id, year))
    conn.commit()
    conn.close()

# create_tables()

def initialize_data():
    # Add programs
    programs = ["Engineering", "Business Administration", "Health Sciences", "Environmental Studies", "Fine Arts"]
    for program in programs:
        add_program(program)

    # Add branches for each program
    branches = {
        "Engineering": ["Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Computer Science", "Chemical Engineering"],
        "Business Administration": ["Finance", "Marketing", "Human Resources", "Operations Management", "International Business"],
        "Health Sciences": ["Nursing", "Pharmacy", "Public Health", "Physiotherapy", "Biomedical Science"],
        "Environmental Studies": ["Environmental Science", "Environmental Policy", "Sustainable Development", "Conservation Biology", "Climate Science"],
        "Fine Arts": ["Visual Arts", "Performing Arts", "Music", "Dance", "Theatre"]
    }
    conn = sqlite3.connect('elite.db')
    conn = conn.cursor()
    for program_name, program_branches in branches.items():
        conn.execute('SELECT id FROM programs WHERE program_name = ?', (program_name,))
        program_id = conn.fetchone()[0]
        for branch in program_branches:
            add_branch(program_id, branch)
    conn.close()

    # Sample events for 2024
    sample_events = [
       # January
       ('New Year Celebration', 'Celebrate the start of the new year.', '2024-01-01', '12:00 AM - 12:00 AM', 'new_year.jpg'),
       ('Republic Day Celebration', 'Celebrate Republic Day with a flag hoisting ceremony.', '2024-01-26', '8:00 AM - 10:00 AM', 'republic_day.jpg'),
       ('Makarsankranti / Pongal', 'Celebrate the harvest festival.', '2024-01-14', '10:00 AM - 1:00 PM', 'makarsankranti.jpg'),

       # March
       ('Parent-Teacher Conference', 'Discuss your child’s progress.', '2024-03-15', '4:00 PM - 6:00 PM', 'parent_teacher.jpg'),
       ('Holi Festival', 'Celebrate the vibrant festival of Holi.', '2024-03-25', '11:00 AM - 2:00 PM', 'holi.jpg'),
       ('Ugadi / Gudi Padwa / Telugu New Year', 'Celebrate the new year according to the Hindu calendar.', '2024-03-30', '10:00 AM - 1:00 PM', 'ugadi.jpg'),

       # April
       ('Eid al-Fitr Celebration', 'Celebrate the end of Ramadan.', '2024-04-10', '12:00 PM - 2:00 PM', 'Ramadan.jpg'),
       ('Spring Concert', 'Enjoy performances by the school choir and band.', '2024-04-10', '7:00 PM - 9:00 PM', 'spring_concert.jpg'),

       # May
       ('Science Fair', 'View student science projects.', '2024-05-20', '9:00 AM - 12:00 PM', 'science_fair.jpg'),
       ('Ethnic Day', 'Showcase traditional attire from different cultures.', '2024-05-25', '10:00 AM - 1:00 PM', 'ethnic_day.jpg'),

       # June
       ('Sports Day', 'Join us for a day of fun and games.', '2024-06-15', '10:00 AM - 3:00 PM', 'sports_day.jpg'),
       ('Eid al-Adha Event', 'Celebrate Eid al-Adha with traditional meals.', '2024-06-17', '1:00 PM - 3:00 PM', 'eid.jpg'),

       # August
       ('Independence Day Celebration', 'Celebrate Independence Day with a flag hoisting ceremony.', '2024-08-15', '8:00 AM - 10:00 AM', 'independence_day.jpg'),
       ('Ganesh Chaturthi', 'Celebrate the festival of Ganesh Chaturthi.', '2024-08-22', '10:00 AM - 1:00 PM', 'ganesh_chaturthi.jpg'),

       # September
       ('Farewell Party', 'Bid farewell to the graduating students.', '2024-09-05', '5:00 PM - 8:00 PM', 'farewell.jpg'),

       # October
       ('Voting Day', 'Participate in the school elections.', '2024-10-10', '9:00 AM - 5:00 PM', 'voting_day.jpg'),
       ('Movie Day', 'Enjoy a movie screening at the school.', '2024-10-20', '3:00 PM - 6:00 PM', 'movie_day.jpg'),
       ('Dusshera', 'Celebrate the victory of good over evil.', '2024-10-24', '10:00 AM - 1:00 PM', 'dusshera.jpg'),
       ('Halloween Parade', 'Students can dress up in costumes.', '2024-10-31', '1:00 PM - 3:00 PM', 'halloween_parade.jpg'),

       # November
       ('Diwali', 'Celebrate the festival of lights.', '2024-11-12', '5:00 PM - 9:00 PM', 'diwali.jpg'),

       # December
       ('Graduation Party', 'Celebrate the achievements of the graduates.', '2024-12-10', '6:00 PM - 9:00 PM', 'graduation.jpg'),
       ('Christmas Celebration', 'Join our Christmas celebration.', '2024-12-15', '5:00 PM - 8:00 PM', 'christmas.jpg'),
       ('Winter Concert', 'Enjoy holiday music performances.', '2024-12-15', '7:00 PM - 9:00 PM', 'winter_concert.jpg')
    ]

    for event in sample_events:
        add_event(*event)  # Unpack the tuple into separate arguments
    conn.close()

# initialize_data()

#home
@app.route('/')
def home():
    return render_template('home.html')

# Add other routes for the application
@app.route('/about')
def about():
    return render_template('about.html')

#faculty
@app.route('/faculty')
def faculty():
    return render_template('faculty.html')

#contact
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    message = request.form['message']

    # Save to the database
    conn = sqlite3.connect('elite.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO contacts (name, email, phone, address, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, phone, address, message))
    conn.commit()
    conn.close()

    flash('Your contact details were submitted successfully.', 'success')
    return redirect(url_for('home'))

#student login
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    error_msg = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = sqlite3.connect('elite.db')
        c = conn.cursor()

        if username and password:
            c.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                      (username, password))
            user = c.fetchone()
            conn.close()

            if user:
                return redirect(url_for('student_dashboard', username=username, student_id=user[3]))

        conn.close()
        error_msg = 'Invalid credentials. Would you like to sign up?'
        return render_template('student_login.html', error_msg=error_msg)
    return render_template('student_login.html', error_msg=error_msg)

#student signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        dob = request.form.get('dob', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        program_id = request.form.get('program')
        branch_id = request.form.get('branch')
        year_of_study = request.form.get('year_of_study')

        conn = sqlite3.connect('elite.db')
        c = conn.cursor()
        try:
            c.execute('SELECT id FROM branches WHERE id = ? AND program_id = ?', (branch_id, program_id))
            if c.fetchone() is None:
                return render_template('signup.html', error_msg='Please select a valid branch for the selected program.', programs=query_db('SELECT * FROM programs ORDER BY id'))

            c.execute('SELECT 1 FROM users WHERE username = ?', (username,))
            if c.fetchone():
                return render_template('signup.html', error_msg='That username is already in use.', programs=query_db('SELECT * FROM programs ORDER BY id'))

            conn.execute('BEGIN IMMEDIATE')
            student_id = generate_student_id(conn, program_id, branch_id)
            c.execute('''
                INSERT INTO users (username, password, student_id, dob, email, phone, address, program_id, branch_id, year_of_study)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, student_id, dob, email, phone, address, program_id, branch_id, year_of_study))
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

        flash('Signup successful. You can now log in with your username and password.', 'success')
        return redirect(url_for('student_login'))

    programs = query_db('SELECT * FROM programs ORDER BY id')
    return render_template('signup.html', programs=programs)

#parent login
@app.route('/parent_login', methods=['GET', 'POST'])
def parent_login():
    error_msg = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = sqlite3.connect('elite.db')
        c = conn.cursor()
        c.execute('SELECT * FROM parents WHERE username = ? AND password = ?',
                  (username, password))
        parent = c.fetchone()
        conn.close()

        if parent:
            return redirect(url_for('parent_dashboard', username=username, student_id=parent[5]))
        else:
            error_msg = 'Invalid credentials. Would you like to sign up?'
            return render_template('parent_login.html', error_msg=error_msg)
    return render_template('parent_login.html', error_msg=error_msg)

#parent signup
@app.route('/parent_signup', methods=['GET', 'POST'])
def parent_signup():
    error_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        parent_type = request.form['parent_type']

        conn = sqlite3.connect('elite.db')
        c = conn.cursor()

        # Insert new parent without checking for existing student ID
        c.execute('''
            INSERT INTO parents (username, password, email, phone, student_id, student_name, parent_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, email, phone, student_id, student_name, parent_type))
        conn.commit()
        conn.close()

        return redirect(url_for('parent_login'))

    return render_template('parent_signup.html', error_msg=error_msg)

#faculty login
@app.route('/faculty_login', methods=['GET', 'POST'])
def faculty_login():
    error_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username and not password:
            error_msg = 'Username and password are required.'

        else:
            conn = sqlite3.connect('elite.db')
            c = conn.cursor()
            c.execute('SELECT * FROM faculty WHERE username = ? AND password = ?', (username, password))
            faculty = c.fetchone()
            conn.close()

            if faculty:
                return redirect(url_for('faculty_dashboard', username=username))
            else:
                error_msg = 'Invalid credentials. Would you like to sign up?.'
            programs = query_db('SELECT * FROM programs ORDER BY id')
            return render_template('faculty_signup.html', error_msg=error_msg, programs=programs)

    error_msg = 'Invalid credentials. Would you like to sign up?.'
    return render_template('faculty_login.html', error_msg=error_msg)

#faculty signup
@app.route('/faculty_signup', methods=['GET', 'POST'])
def faculty_signup():
    conn = sqlite3.connect('elite.db')
    c = conn.cursor()

    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['phone']
            program_id = request.form['program']
            branch_id = request.form['branch']
            teaching_year = request.form['teaching_year']
            subject_id = request.form['subject_id']

            # Check if the faculty member already exists
            c.execute('SELECT * FROM faculty WHERE username = ? OR email = ?', (username, email))
            existing_user = c.fetchone()

            if existing_user:
                programs = c.execute('SELECT * FROM programs ORDER BY id').fetchall()
                return render_template('faculty_signup.html', programs=programs, error_msg='That username or email is already in use.')

            c.execute('SELECT id FROM branches WHERE id = ? AND program_id = ?', (branch_id, program_id))
            if c.fetchone() is None:
                programs = c.execute('SELECT * FROM programs ORDER BY id').fetchall()
                return render_template('faculty_signup.html', programs=programs, error_msg='Please select a valid branch for the selected program.')

            c.execute('SELECT id FROM subjects WHERE id = ? AND branch_id = ? AND year = ?',
                      (subject_id, branch_id, teaching_year))
            if c.fetchone() is None:
                programs = c.execute('SELECT * FROM programs ORDER BY id').fetchall()
                return render_template('faculty_signup.html', programs=programs, error_msg='Please select a valid subject for the selected branch and year.')

            # Insert the new faculty member into the database
            c.execute('''
                INSERT INTO faculty (username, password, email, phone, program_id, branch_id, subject_id, teaching_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, email, phone, program_id, branch_id, subject_id, teaching_year))
            conn.commit()

            return redirect(url_for('faculty_login'))

        # Fetch the programs for the dropdown list
        programs = c.execute('SELECT * FROM programs').fetchall()
        return render_template('faculty_signup.html', programs=programs)

    finally:
        conn.close()

# Define admin
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin_password')

#admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate username and password
        if not username:
            error_msg = 'Username is required.'
            return render_template('admin_login.html', error_msg=error_msg)
        if not password:
            error_msg = 'Password is required.'
            return render_template('admin_login.html', error_msg=error_msg)

        # Check against hard-coded credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for('admin_dashboard', username=username))
        else:
            error_msg = 'Invalid credentials.'
            return render_template('admin_login.html', error_msg=error_msg)

    return render_template('admin_login.html', error_msg=error_msg)

#student dash
@app.route('/student_dashboard')
def student_dashboard():
    username = request.args.get('username')

    if not username:
        return redirect(url_for('student_login'))

    programs = {
        1: 'Engineering',
        2: 'Business',
        3: 'Health Science',
        4: 'Environmental Studies',
        5: 'Fine Arts'
    }

    branches = {
        1: 'Mechanical Engineering',
        2: 'Electrical Engineering',
        3: 'Civil Engineering',
        4: 'Computer Science',
        5: 'Chemical Engineering',
        6: 'Finance',
        7: 'Marketing',
        8: 'Human Resources',
        9: 'Operations Management',
        10: 'International Business',
        11: 'Nursing',
        12: 'Pharmacy',
        13: 'Public Health',
        14: 'Physiotherapy',
        15: 'Biomedical Science',
        16: 'Environmental Science',
        17: 'Environmental Policy',
        18: 'Sustainable Development',
        19: 'Conservation Biology',
        20: 'Climate Science',
        21: 'Visual Arts',
        22: 'Performing Arts',
        23: 'Music',
        24: 'Dance',
        25: 'Theatre'
    }

    conn = None
    try:
        conn = sqlite3.connect('elite.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT users.*, programs.program_name, branches.branch_name
            FROM users
            LEFT JOIN programs ON programs.id = users.program_id
            LEFT JOIN branches ON branches.id = users.branch_id
            WHERE users.username = ?
        ''', (username,))
        student = cursor.fetchone()

        if student:
            student_id = student['student_id']
            cursor.execute('SELECT * FROM parents WHERE student_id=?', (student_id,))
            parents = cursor.fetchall()

            cursor.execute('SELECT title, description, date, time, image_url FROM events WHERE date LIKE "2024%" ORDER BY date, time')
            events = cursor.fetchall()

            cursor.execute('SELECT faculty_username, message, timestamp FROM notifications WHERE student_id = ?', (student_id,))
            notifications = cursor.fetchall()

            # Fetch subjects based on student's branch and year
            cursor.execute('SELECT subject_name FROM subjects WHERE branch_id=? AND year=?', (student['branch_id'], student['year_of_study']))
            subjects = cursor.fetchall()

            program_name = student['program_name'] or "Unknown Program"
            branch_name = student['branch_name'] or "Unknown Branch"

            return render_template('student_dashboard.html', student=student, parents=parents, events=events, program_name=program_name, branch_name=branch_name, notifications=notifications, subjects=subjects)
        else:
            return redirect(url_for('student_login'))
    finally:
        if conn:
            conn.close()

#parent dash
@app.route('/parent_dashboard')
def parent_dashboard():
    username = request.args.get('username')
    student_id = request.args.get('student_id')

    programs = {
        1: 'Engineering',
        2: 'Business',
        3: 'Health Science',
        4: 'Environmental Studies',
        5: 'Fine Arts'
    }

    branches = {
        1: 'Mechanical Engineering',
        2: 'Electrical Engineering',
        3: 'Civil Engineering',
        4: 'Computer Science',
        5: 'Chemical Engineering',
        6: 'Finance',
        7: 'Marketing',
        8: 'Human Resources',
        9: 'Operations Management',
        10: 'International Business',
        11: 'Nursing',
        12: 'Pharmacy',
        13: 'Public Health',
        14: 'Physiotherapy',
        15: 'Biomedical Science',
        16: 'Environmental Science',
        17: 'Environmental Policy',
        18: 'Sustainable Development',
        19: 'Conservation Biology',
        20: 'Climate Science',
        21: 'Visual Arts',
        22: 'Performing Arts',
        23: 'Music',
        24: 'Dance',
        25: 'Theatre'
    }

    if not username or not student_id:
        return redirect(url_for('parent_login'))

    try:
        conn = sqlite3.connect('elite.db')
        cursor = conn.cursor()

        # Fetch parent details
        cursor.execute('SELECT * FROM parents WHERE username=? AND student_id=?', (username, student_id))
        parents = cursor.fetchone()

        if parents:
            # Fetch student details
            cursor.execute('SELECT * FROM users WHERE student_id=?', (student_id,))
            student = cursor.fetchone()
            program_name = programs.get(student[8], "Unknown Program")
            branch_name = branches.get(student[9], "Unknown Branch")

            # Fetch events for 2024
            cursor.execute('SELECT title, description, date, time, image_url FROM events WHERE date LIKE "2024%" ORDER BY date, time')
            events = cursor.fetchall()
            return render_template('parent_dashboard.html', parents=parents, student=student, events=events,program_name=program_name,branch_name=branch_name)
        else:
            return redirect(url_for('parent_login'))

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        parents = None
        student = None
        events = []
    finally:
        conn.close()

    return render_template('parent_dashboard.html', parents=parents, student=student, events=events)

#faculty dash
@app.route('/faculty_dashboard', methods=['GET'])
def faculty_dashboard():
    # Get the faculty's username dynamically from query parameters or session
    username = request.args.get('username')  # Or use session if logged in

    if not username:
        return redirect(url_for('faculty_login'))

    try:
        conn = sqlite3.connect('elite.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Fetch the faculty member's details based on the username
        c.execute('''
            SELECT faculty.*, programs.program_name, branches.branch_name, subjects.subject_name
            FROM faculty
            LEFT JOIN programs ON programs.id = faculty.program_id
            LEFT JOIN branches ON branches.id = faculty.branch_id
            LEFT JOIN subjects ON subjects.id = faculty.subject_id
            WHERE faculty.username = ?
        ''', (username,))
        faculty = c.fetchone()

        if faculty:
            # Fetch events for the year 2024
            c.execute('SELECT title, description, date, time, image_url FROM events WHERE date LIKE "2024%" ORDER BY date, time')
            events = c.fetchall()

            program_name = faculty['program_name'] or "Unknown Program"
            branch_name = faculty['branch_name'] or "Unknown Branch"
            subject_name = faculty['subject_name'] or "Not assigned"

            branch_id = faculty['branch_id']

            # Fetch student details grouped by year in the branch
            first_year_students = c.execute(
                'SELECT * FROM users WHERE branch_id = ? AND year_of_study = 1',
                (branch_id,)
            ).fetchall()

            second_year_students = c.execute(
                'SELECT * FROM users WHERE branch_id = ? AND year_of_study = 2',
                (branch_id,)
            ).fetchall()

            third_year_students = c.execute(
                'SELECT * FROM users WHERE branch_id = ? AND year_of_study = 3',
                (branch_id,)
            ).fetchall()

            fourth_year_students = c.execute(
                'SELECT * FROM users WHERE branch_id = ? AND year_of_study = 4',
                (branch_id,)
            ).fetchall()
            first_year_total = len(first_year_students)
            second_year_total = len(second_year_students)
            third_year_total = len(third_year_students)
            fourth_year_total = len(fourth_year_students)

            second_year_subjects = c.execute('''
                SELECT subject_name
                FROM subjects
                WHERE branch_id = ? AND year = 2
                ORDER BY subject_name
            ''', (branch_id,)).fetchall()
            # Count total students in the faculty's branch
            total_students = c.execute('SELECT COUNT(*) FROM users WHERE branch_id = ?', (branch_id,)).fetchone()[0]
            sent_notifications = c.execute('''
                SELECT COUNT(*) AS recipient_count, message, timestamp
                FROM notifications
                WHERE faculty_username = ?
                GROUP BY message, timestamp
                ORDER BY timestamp DESC
            ''', (username,)).fetchall()

            return render_template('faculty_dashboard.html', events=events, faculty=faculty, program_name=program_name, branch_name=branch_name, total_students=total_students,
                                   first_year_students=first_year_students, second_year_students=second_year_students, third_year_students=third_year_students, fourth_year_students=fourth_year_students,
                                   first_year_total=first_year_total, second_year_total=second_year_total, third_year_total=third_year_total, fourth_year_total=fourth_year_total,
                                   subject_name=subject_name, second_year_subjects=second_year_subjects, sent_notifications=sent_notifications)
        else:
            return redirect(url_for('faculty_login'))
    finally:
        conn.close()

#admin dash
@app.route('/admin_dashboard')
def admin_dashboard():
    conn = sqlite3.connect('elite.db')
    cursor = conn.cursor()

    # Fetch and map programs and branches
    programs = {row[0]: row[1] for row in cursor.execute('SELECT id, program_name FROM programs').fetchall()}
    branches = {row[0]: row[1] for row in cursor.execute('SELECT id, branch_name FROM branches').fetchall()}

    # Fetch subjects grouped by branch and year
    query = """
    SELECT branch_id, year, subject_name
    FROM subjects
    ORDER BY branch_id, year, subject_name;
    """
    cursor.execute(query)
    subjects = cursor.fetchall()

    organized_subjects = {}
    for branch_id, year, subject_name in subjects:
        branch_name = branches.get(branch_id, "Unknown Branch")
        if branch_name not in organized_subjects:
            organized_subjects[branch_name] = {}
        if year not in organized_subjects[branch_name]:
            organized_subjects[branch_name][year] = []
        organized_subjects[branch_name][year].append(subject_name)

    # Fetch students with program and branch names
    students = cursor.execute('SELECT * FROM users').fetchall()
    mapped_students = []
    for student in students:
        student = list(student)  # Convert tuple to list to allow modifications
        student[8] = programs.get(student[8], "Unknown Program")  # Replace program ID with program name
        student[9] = branches.get(student[9], "Unknown Branch")   # Replace branch ID with branch name
        mapped_students.append(student)

    # Fetch faculty with program and branch names
    faculty_members = cursor.execute('SELECT * FROM faculty').fetchall()
    mapped_faculty = []
    for faculty in faculty_members:
        faculty = list(faculty)  # Convert tuple to list to allow modifications
        faculty[5] = programs.get(faculty[5], "Unknown Program")  # Replace program ID with program name
        faculty[6] = branches.get(faculty[6], "Unknown Branch")   # Replace branch ID with branch name
        mapped_faculty.append(faculty)

    contacts = cursor.execute('SELECT * FROM contacts').fetchall()

    # Fetch events
    cursor.execute('SELECT title, description, date, time, image_url FROM events WHERE date LIKE "2024%" ORDER BY date, time')
    events = cursor.fetchall()

    notifications = cursor.execute('''
        SELECT faculty_username, message, timestamp, COUNT(*) AS recipient_count
        FROM notifications
        GROUP BY faculty_username, message, timestamp
        ORDER BY timestamp DESC
    ''').fetchall()

    # Get total counts
    total_students = cursor.execute('SELECT COUNT(*) AS count FROM users').fetchone()[0]
    total_faculty = cursor.execute('SELECT COUNT(*) AS count FROM faculty').fetchone()[0]
    total_programs = cursor.execute('SELECT COUNT(*) AS count FROM programs').fetchone()[0]
    total_branches = cursor.execute('SELECT COUNT(*) AS count FROM branches').fetchone()[0]

    conn.close()

    return render_template(
        'admin_dashboard.html',
        students=mapped_students,
        faculty_members=mapped_faculty,
        events=events,
        total_students=total_students,
        total_faculty=total_faculty,
        total_programs=total_programs,
        total_branches=total_branches,
        subjects=organized_subjects,
        contacts=contacts,
        notifications=notifications
    )

#Delete Contact
@app.route('/delete_contact/<string:name>', methods=['POST'])
def delete_contact(name):
    try:
        conn = sqlite3.connect('elite.db')
        cursor = conn.cursor()

        # Delete the contact from the 'contacts' table using the 'name'
        cursor.execute('DELETE FROM contacts WHERE name = ?', (name,))
        conn.commit()

        # Check if the contact was deleted, if not, return a 404
        if cursor.rowcount == 0:
            return f"No contact found with name: {name}", 404

        # Redirect to the admin dashboard after successful deletion
        return redirect(url_for('admin_dashboard'))

    except Exception as e:
        # Handle any database or other errors
        return str(e), 500

    finally:
        # Close the connection to the database
        conn.close()

#add student from the admin
@app.route('/add_student', methods=['POST'])
def add_student():
    username = request.form.get('username')
    password = request.form.get('password')
    student_id = request.form.get('student_id')
    dob = request.form.get('dob')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    program_id = request.form.get('program')
    branch_id = request.form.get('branch')
    year_of_study = request.form.get('year_of_study')

    conn = sqlite3.connect('elite.db')
    conn.execute('INSERT INTO users (username, password, student_id, dob, email, phone, address, program_id, branch_id, year_of_study) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (username, password, student_id, dob, email, phone, address, program_id, branch_id, year_of_study))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

#edit student from the admin
@app.route('/update_student', methods=['POST'])
def update_student():
    username = request.form['username']
    password = request.form['password']
    student_id = request.form['student_id']
    dob = request.form['dob']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    program_id = request.form['program']
    branch_id = request.form['branch']
    year_of_study = request.form['year_of_study']

    conn = sqlite3.connect('elite.db')
    try:
        conn.execute('UPDATE users SET username = ?, password = ?, dob = ?, email = ?, phone = ?, address = ?, program_id = ?, branch_id = ?, year_of_study = ? WHERE student_id = ?',
                     (username, password, dob, email, phone, address, program_id, branch_id, year_of_study, student_id))
        conn.commit()

    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

#delete student from admin
@app.route('/delete_student/<student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        conn = sqlite3.connect('elite.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM users WHERE student_id = ?', (student_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return f"No student found with student_id: {student_id}", 404

        return redirect(url_for('admin_dashboard'))

    except Exception as e:
        return str(e), 500

    finally:
        conn.close()

#edit faculty from admin
@app.route('/update_faculty', methods=['POST'])
def update_faculty():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    phone = request.form.get('phone')
    program_id = request.form.get('program')
    branch_id = request.form.get('branch')

    conn = sqlite3.connect('elite.db')
    try:
        conn.execute('UPDATE faculty SET password = ?, email = ?, phone = ?, program_id = ?, branch_id = ? WHERE username = ?',
                     (password, email, phone, program_id, branch_id, username))
        conn.commit()

    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

#edit faculty from admin
@app.route('/add_faculty', methods=['POST'])
def add_faculty():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    phone = request.form.get('phone')
    program_id = request.form.get('program')
    branch_id = request.form.get('branch')

    conn = sqlite3.connect('elite.db')
    try:
        conn.execute('INSERT INTO faculty (username, password, email, phone, program_id, branch_id) VALUES (?, ?, ?, ?, ?, ?)',
                     (username, password, email, phone, program_id, branch_id))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

#delete faculty from the admin
@app.route('/delete_faculty/<username>', methods=['POST'])
def delete_faculty(username):
    try:
        # Connect to the database
        conn = sqlite3.connect('elite.db')
        cursor = conn.cursor()

        # Execute the delete operation
        cursor.execute('DELETE FROM faculty WHERE username = ?', (username,))

        # Commit changes
        conn.commit()

        # Check if any row was deleted
        if cursor.rowcount == 0:
            return f"No faculty found with username: {username}", 404

        return redirect(url_for('admin_dashboard'))

    except Exception as e:
        # Handle exceptions and display error
        return str(e), 500

    finally:
        # Close the database connection
        conn.close()

#Notification
@app.route('/send_notification', methods=['POST'])
def send_notification():
    student_id = request.form.get('student_id')
    faculty_username = request.form.get('faculty_username')
    message = request.form.get('message', '').strip()
    send_all = request.form.get('send_all')  # Checkbox value
    target_year = request.form.get('target_year')  # Year parameter

    try:
        conn = sqlite3.connect('elite.db')
        cursor = conn.cursor()

        # Fetch branch_id of the faculty
        cursor.execute('SELECT branch_id FROM faculty WHERE username = ?', (faculty_username,))
        branch = cursor.fetchone()

        if not branch:
            return jsonify({"status": "error", "message": "Error: Faculty branch not found"})

        if not message:
            return jsonify({"status": "error", "message": "Notification message is required"})

        branch_id = branch[0]

        # Check if 'send_all' is selected
        if send_all:
            # Fetch all students in the faculty's branch
            cursor.execute('SELECT student_id FROM users WHERE branch_id = ?', (branch_id,))
            student_ids = cursor.fetchall()

            if not student_ids:
                return jsonify({"status": "error", "message": "No students found in the branch"})

            # Insert notifications for all students
            for student in student_ids:
                cursor.execute('''INSERT INTO notifications (student_id, faculty_username, message)
                                  VALUES (?, ?, ?)''', (student[0], faculty_username, message))

        # If a specific year is targeted
        elif target_year:
            # Fetch all students in the specified year and faculty's branch
            cursor.execute('''SELECT student_id FROM users
                              WHERE branch_id = ? AND year_of_study = ?''', (branch_id, target_year))
            student_ids = cursor.fetchall()

            if not student_ids:
                return jsonify({"status": "error", "message": "No students found in the specified year"})

            # Insert notifications for students in the specified year
            for student in student_ids:
                cursor.execute('''INSERT INTO notifications (student_id, faculty_username, message)
                                  VALUES (?, ?, ?)''', (student[0], faculty_username, message))  # Corrected index

        else:
            # Ensure student_id is only required if not sending to all or targeting a year
            if not student_id:
                return jsonify({"status": "error", "message": "Student ID is required if not sending to all or targeting a year"})

            cursor.execute('SELECT 1 FROM users WHERE student_id = ? AND branch_id = ?', (student_id, branch_id))
            if cursor.fetchone() is None:
                return jsonify({"status": "error", "message": "Student is not in this faculty branch"})

            # Insert notification for specific student
            cursor.execute('''INSERT INTO notifications (student_id, faculty_username, message)
                              VALUES (?, ?, ?)''', (student_id, faculty_username, message))

        conn.commit()
        return jsonify({"status": "success", "message": "Notification sent successfully"})

    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})

    finally:
        conn.close()

#logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/programs')
def programs():
    programs = query_db('SELECT * FROM programs')
    return render_template('programs.html', programs=programs)

@app.route('/branches/<int:program_id>')
def branches(program_id):
    program = query_db('SELECT * FROM programs WHERE id = ?', [program_id], one=True)
    branches = query_db('SELECT * FROM branches WHERE program_id = ?', [program_id])
    return render_template('branches.html', program=program, branches=branches)

@app.route('/get_branches/<int:program_id>')
def get_branches(program_id):
    branches = query_db('SELECT * FROM branches WHERE program_id = ?', [program_id])
    branches_list = [{'id': branch['id'], 'branch_name': branch['branch_name']} for branch in branches]
    return jsonify(branches_list)


@app.route('/get_subjects/<int:branch_id>/<int:year>')
def get_subjects(branch_id, year):
    subjects = query_db(
        'SELECT id, subject_name FROM subjects WHERE branch_id = ? AND year = ? ORDER BY subject_name',
        [branch_id, year]
    )
    return jsonify([{'id': subject['id'], 'subject_name': subject['subject_name']} for subject in subjects])

# Registration
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        program_id = request.form['program']
        branch_id = request.form['branch']
        enrollment_year = request.form['year']

        # Insert data into the student table
        conn = sqlite3.connect('elite.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO student (name, email, phone, program_id, branch_id, enrollment_year)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, program_id, branch_id, enrollment_year))

        conn.commit()
        conn.close()

        flash('Registration successful!')
        return redirect(url_for('registration'))

    programs = query_db('SELECT * FROM programs ORDER BY id')
    return render_template('registration.html', programs=programs)

#event
@app.route('/events', methods=['GET'])
def get_events():
    try:
        conn = sqlite3.connect('elite.db')
        c = conn.cursor()
        c.execute('SELECT * FROM events WHERE date LIKE "2024%" ORDER BY date, time')
        sample_events = c.fetchall()
        conn.close()

        event_list = [
            {'id': event[0], 'title': event[1], 'description': event[2], 'date': event[3], 'time': event[4], 'image_url': event[5]}
            for event in sample_events
        ]

        return jsonify(event_list)

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500


def load_program_data(program_name):
    with open(f'data/{program_name}.json') as f:
        return json.load(f)

@app.route('/business')
def business():
    return render_template('business.html')

@app.route('/engineering')
def engineering():
    return render_template('engineering.html')

@app.route('/finearts')
def finearts():
    return render_template('finearts.html')

@app.route('/environmental')
def environmental():
    return render_template('environmental.html')

@app.route('/healthscience')
def healthscience():
    return render_template('healthscience.html')

@app.route('/program/<program_name>')
def program(program_name):
    program_details = load_program_data(program_name)
    return render_template('program.html', program=program_details)

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/campus_life')
def campus_life():
    return render_template('campus_life.html')

@app.route('/campus_life/housing_dining')
def housing_dining():
    return render_template('housing_dining.html')

@app.route('/campus_life/health_wellness')
def health_wellness():
    return render_template('health_wellness.html')

@app.route('/campus_life/campus_safety')
def campus_safety():
    return render_template('campus_safety.html')

@app.route('/campus_life/athletics')
def athletics():
    return render_template('athletics.html')

@app.route('/campus_life/arts_culture')
def arts_culture():
    return render_template('arts_culture.html')

@app.route('/campus-map')
def campus_map():
    return render_template('campus_map.html')


if __name__ == '__main__':
    app.run(debug=True)