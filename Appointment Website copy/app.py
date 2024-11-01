from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for sessions

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'your_mysql_user',          # Replace with your MySQL username
    'password': 'your_mysql_password',  # Replace with your MySQL password
    'database': 'exam_system'            # Ensure you have this database created
}

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Authentication system
class StudentAuthSystem:
    def login(self, username, password):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return "Invalid account. Please check your username."
        
        if user["login_attempts"] >= 3:
            cursor.close()
            conn.close()
            return "Account locked. Please contact the admin to reset."
        
        # Check the hashed password
        if check_password_hash(user["password"], password):
            cursor.execute("UPDATE users SET login_attempts = 0 WHERE username = %s", (username,))
            conn.commit()
            message = "Login successful!"
        else:
            cursor.execute("UPDATE users SET login_attempts = login_attempts + 1 WHERE username = %s", (username,))
            conn.commit()
            message = "Invalid password/account. Please try again."

        cursor.close()
        conn.close()
        return message

    def register_user(self, username, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)  # Hash the password for security
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            message = "Account created successfully!"
        except mysql.connector.IntegrityError:
            message = "Username already exists."
        finally:
            cursor.close()
            conn.close()
        return message

# Exam registration system
class ExamRegistrationSystem:
    def register_exam(self, username, exam_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM registrations WHERE username = %s", (username,))
        count = cursor.fetchone()[0]

        if count >= 3:
            cursor.close()
            conn.close()
            return "Maximum registration limit reached. Cannot register for more than 3 exams."

        cursor.execute("INSERT INTO registrations (username, exam_name) VALUES (%s, %s)", (username, exam_name))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Registration successful for {exam_name}!"

    def view_registered_exams(self, username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT exam_name FROM registrations WHERE username = %s", (username,))
        exams = [row["exam_name"] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return exams if exams else "No exams registered."

    def cancel_registration(self, username, exam_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registrations WHERE username = %s AND exam_name = %s", (username, exam_name))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Registration for {exam_name} canceled."

# Initialize the systems
auth_system = StudentAuthSystem()
exam_system = ExamRegistrationSystem()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        message = auth_system.register_user(username, password)
        flash(message)
        if "successfully" in message:
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        message = auth_system.login(username, password)
        if "successful" in message:
            session['username'] = username
            flash(message)
            return redirect(url_for('appointment'))
        flash(message)
    return render_template('login.html')

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'username' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        exam_name = request.form['exams']
        message = exam_system.register_exam(session['username'], exam_name)
        flash(message)
    
    registered_exams = exam_system.view_registered_exams(session['username'])
    return render_template('appointment.html', registered_exams=registered_exams)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
