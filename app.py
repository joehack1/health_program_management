from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret254'

# Database connection
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# Create doctors table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

# Home
@app.route('/')
def home():
    if 'doctor_id' not in session:
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('login'))
    
    username = session.get('username')
    return render_template('home.html', username=username)

# Doctor Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        c.execute('SELECT id FROM doctors WHERE username = ? AND password = ?', (username, password))
        doctor = c.fetchone()
        if doctor:
            session['doctor_id'] = doctor[0]
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# Doctor Logout (only once)
@app.route('/logout')
def logout():
    session.pop('doctor_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Create Health Program
@app.route('/program/create', methods=['GET', 'POST'])
def create_program():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        try:
            c.execute('INSERT INTO programs (name) VALUES (?)', (name,))
            conn.commit()
            flash('Health program created successfully!', 'success')
            return redirect(url_for('home'))
        except:
            flash('Program already exists.', 'danger')
            return redirect(url_for('home'))
    return render_template('create_program.html')

# Register Client
@app.route('/client/register', methods=['GET', 'POST'])
def register_client():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        c.execute('INSERT INTO clients (name, age, gender) VALUES (?, ?, ?)', (name, age, gender))
        conn.commit()
        flash('Client registered successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('register_client.html')

# Enroll Client
@app.route('/enroll', methods=['GET', 'POST'])
def enroll_client():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        client_id = request.form['client_id']
        program_ids = request.form.getlist('program_ids')
        for pid in program_ids:
            c.execute('INSERT INTO enrollments (client_id, program_id) VALUES (?, ?)', (client_id, pid))
        conn.commit()
        flash('Client enrolled successfully!', 'success')
        return redirect(url_for('home'))

    c.execute('SELECT id, name FROM clients')
    clients = c.fetchall()
    c.execute('SELECT id, name FROM programs')
    programs = c.fetchall()
    return render_template('enroll_client.html', clients=clients, programs=programs)

# Search Clients
@app.route('/client/search', methods=['GET', 'POST'])
def search_client():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_name = request.form['name']
        c.execute('SELECT * FROM clients WHERE name LIKE ?', ('%' + search_name + '%',))
        results = c.fetchall()
        return render_template('search_client.html', results=results)
    return render_template('search_client.html')

# View Client Profile
@app.route('/client/<int:client_id>')
def client_profile(client_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))

    c.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    client = c.fetchone()
    c.execute('''
        SELECT programs.name FROM enrollments 
        JOIN programs ON enrollments.program_id = programs.id
        WHERE enrollments.client_id = ?
    ''', (client_id,))
    programs = [row[0] for row in c.fetchall()]
    return render_template('client_profile.html', client=client, programs=programs)

@app.route('/register_doctor', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO doctors (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        flash('Doctor registered successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register_doctor.html')

if __name__ == '__main__':
    app.run(debug=True)
