import sqlite3

def initializ_db():
    conn = sqlite3.connect('elite.db')
    c = conn.cursor()

    # Create users table
    c.execute('''
              CREATE TABLE IF NOT EXISTS users
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
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
              FOREIGN KEY (branch_id) REFERENCES branches(id))
              ''')

    # Create parents table
    c.execute('''
              CREATE TABLE IF NOT EXISTS parents
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL,
              email TEXT NOT NULL,
              phone TEXT NOT NULL,
              student_id TEXT NOT NULL,
              student_name TEXT NOT NULL,
              parent_type TEXT NOT NULL);
              ''')

    # Create faculty table
    c.execute('''
            CREATE TABLE IF NOT EXISTS faculty
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL,
              email TEXT NOT NULL,
              phone TEXT NOT NULL,
              program_id INTEGER NOT NULL,
              branch_id INTEGER NOT NULL,
              subject_id INTEGER,
              teaching_year INTEGER,
              FOREIGN KEY (program_id) REFERENCES programs(id),
              FOREIGN KEY (branch_id) REFERENCES branches(id));
              ''')

    faculty_columns = {row[1] for row in c.execute('PRAGMA table_info(faculty)').fetchall()}
    if 'subject_id' not in faculty_columns:
        c.execute('ALTER TABLE faculty ADD COLUMN subject_id INTEGER')
    if 'teaching_year' not in faculty_columns:
        c.execute('ALTER TABLE faculty ADD COLUMN teaching_year INTEGER')

    # Create programs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_name TEXT NOT NULL
        );
    ''')

    # Create branches table with a foreign key to programs
    c.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER NOT NULL,
            branch_name TEXT NOT NULL,
            FOREIGN KEY (program_id) REFERENCES programs(id)
        );
    ''')

    # Create contacts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            message TEXT NOT NULL
        );
    ''')
    #events
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

    # Create contacts table
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

    # Create student registration table
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
    #notifiaction
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            faculty_username TEXT,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(student_id));
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

    #Subject
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            FOREIGN KEY (branch_id) REFERENCES branches(id));
        ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initializ_db()

import sqlite3
def add_subject(branch_id, year, subject_name):
    conn = sqlite3.connect('elite.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO subjects (branch_id, year, subject_name)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM subjects WHERE branch_id = ? AND year = ? AND subject_name = ?
        )
    ''', (branch_id, year, subject_name, branch_id, year, subject_name))
    conn.commit()
    conn.close()

def initialize_data():
    conn = sqlite3.connect('elite.db')
    conn = conn.cursor()
    subjects = [
        ( 4, 1,'Data Structures'),
        ( 4, 1,'Computer Organization'),
        ( 4, 1,'Discrete Mathematics'),
        ( 4, 2,'Algorithms'),
        ( 4, 2, 'Operating Systems'),
        ( 4, 2, 'Database Management Systems'),
        ( 4, 3, 'Theory of Computation'),
        ( 4, 3,'Computer Networks'),

        # Business Administration Subjects
            (2, 1, 'Introduction to Business'),
            (2, 1, 'Principles of Management'),
            (2, 1, 'Accounting Basics'),
            (2, 2, 'Marketing Principles'),
            (2, 2, 'Financial Management'),
            (2, 2, 'Business Law'),
            (2, 3, 'Strategic Management'),
            (2, 3, 'Human Resource Management'),
            (2, 3, 'Operations Management'),
            (2, 4, 'International Business'),
            (2, 4, 'Entrepreneurship'),
            (2, 4, 'Business Ethics'),

            # Health Science Subjects
            (3, 1, 'Human Anatomy'),
            (3, 1, 'Introduction to Health Science'),
            (3, 1, 'Public Health Basics'),
            (3, 2, 'Medical Terminology'),
            (3, 2, 'Health Policy'),
            (3, 2, 'Epidemiology'),
            (3, 3, 'Clinical Practice'),
            (3, 3, 'Health Education'),
            (3, 3, 'Research Methods in Health Science'),
            (3, 4, 'Healthcare Management'),
            (3, 4, 'Advanced Clinical Skills'),
            (3, 4, 'Health Promotion'),

            # Environmental Studies Subjects
            (4, 1, 'Environmental Science'),
            (4, 1, 'Ecology'),
            (4, 1, 'Environmental Policy'),
            (4, 2, 'Climate Change'),
            (4, 2, 'Conservation Biology'),
            (4, 2, 'Environmental Impact Assessment'),
            (4, 3, 'Sustainable Development'),
            (4, 3, 'Environmental Law'),
            (4, 3, 'Resource Management'),
            (4, 4, 'Environmental Health'),
            (4, 4, 'Global Environmental Issues'),
            (4, 4, 'Capstone Project'),

            # Fine Arts Subjects
            (5, 1, 'Art History'),
            (5, 1, 'Drawing Fundamentals'),
            (5, 1, 'Visual Arts Practice'),
            (5, 2, 'Sculpture'),
            (5, 2, 'Painting Techniques'),
            (5, 2, 'Art Theory'),
            (5, 3, 'Printmaking'),
            (5, 3, 'Digital Art'),
            (5, 3, 'Advanced Studio Practice'),
            (5, 4, 'Art Criticism'),
            (5, 4, 'Professional Practices'),
            (5, 4, 'Final Exhibition')

        ]

    for subject in subjects:
        add_subject(*subject)  # Unpack the tuple into separate arguments
    conn.close()


initialize_data()