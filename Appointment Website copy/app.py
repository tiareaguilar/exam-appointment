from flask import Flask, render_template, request, redirect, session, url_for
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Validation functions
def is_valid_name(name):
    return re.fullmatch(r'[a-zA-Z]+', name) is not None

def is_valid_email(email):
    return re.fullmatch(r'[0-9]{10}@student\.csn\.edu', email) is not None

def generate_username(first_name, email):
    nshe_last_four = email[6:10]  # Extract the last four digits of the NSHE number
    return first_name.lower() + nshe_last_four

def is_valid_username(username, first_name, email):
    return username == generate_username(first_name, email)

def is_valid_password(password, email):
    return password == email[:10]

# Routes
@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Clear any previous session messages at the start
    session.pop('messages', None)

    if request.method == 'POST':
        messages = []

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        # Validation checks and feedback messages
        if not is_valid_name(first_name):
            messages.append("First name must only contain letters A-Z")
        if not is_valid_name(last_name):
            messages.append("Last name must only contain letters A-Z")
        if not is_valid_email(email):
            messages.append("Email must be NSHE#@student.csn.edu")
        elif not is_valid_username(username, first_name, email):
            # Updated message to provide format guidance without showing the specific username
            messages.append("Username must be first name and last four of NSHE number")
        if not is_valid_password(password, email):
            messages.append("Password must only contain numbers 0-9")
        
        # Store messages in session if there are errors
        if messages:
            session['messages'] = messages
        else:
            # If all checks pass, redirect without adding a success message
            return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/appointment')
def appointment():
    return render_template('appointment.html')

@app.route('/reservation')
def reservation():
    return render_template('reservation.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
