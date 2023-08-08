# Import required packages
from flask import Flask, render_template, request,  redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle



# Initialize the app
app = Flask(__name__, template_folder='templates')
model = pickle.load(open('model.pkl', 'rb'))


ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:tamazar123*@localhost:3306/user_db'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:tamazar123*@localhost:3306/user_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user_details'
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))


 ####Same as constructor in Java where we use this.
    def __init__(username, password):
        self.username = username
        self.password = password

db.create_all()

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tamazar123*'
app.config['MYSQL_DB'] = 'user_db'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_details WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('loanform.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form  :
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_details WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password :
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user_details VALUES (NULL, % s, % s)', (username, password, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)







@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        gender = request.form[('gender')]
        married = request.form[('married')]
        dependents = request.form[('dependents')]
        education = request.form[('education')]
        self_employed = request.form[('self_employed')]
        applicantincome = request.form[('applicantincome')]
        coapplicantincome = request.form[('coapplicantincome')]
        loan_amount = request.form[('loan_amount')]
        loan_amount_term = request.form[('loan_amount_term')]
        credit_history = request.form[('credit_history')]
        property_area = request.form[('property_area')]

        prediction = model.predict(
            [[gender, married, dependents, education, self_employed, applicantincome, coapplicantincome, loan_amount,
              loan_amount_term, credit_history, property_area]])


        if prediction >= 0.5 :
            return render_template('index.html', prediction_text="Congratulations.!Your loan is Approved.")
        else:
         return render_template('index.html', prediction_text="We are Sorry. Your loan is Not Approved.")



if __name__ == '__main__':
    app.run(debug=True)
