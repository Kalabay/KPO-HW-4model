from flask import Flask, request
import datetime
import hashlib
import jwt
import sqlite3 as sl

app = Flask(__name__)

con = sl.connect('main.db', check_same_thread=False)
con.execute("DROP TABLE IF EXISTS user")
user_id = 0
con.execute("""
        CREATE TABLE user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(10) NOT NULL CHECK (role IN ('customer', 'chef', 'manager')),
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        );
        """)


con.execute("DROP TABLE IF EXISTS session")
session_id = 0
con.execute("""
        CREATE TABLE session (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_token VARCHAR(255) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id)
        );
    """)


@app.route('/register', methods=['POST'])
def register():
    global user_id
    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data or 'password' not in data or 'role' not in data:
        return ({"message": "Invalid request data"}), 400

    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()

    email_exists = (con.execute('SELECT * FROM user WHERE email=?', (data['email'],)).fetchone())
    username_exists = (con.execute('SELECT * FROM user WHERE username=?', (data['username'],)).fetchone())

    if email_exists != None or username_exists != None:
        return ({"message": "User already exists"}), 409

    sql_add_user = 'INSERT INTO user (id, username, email, password_hash, role, ' \
                   'created_at, updated_at) values(?, ?, ?, ?, ?, ?, ?)'

    role = data['role'] if 'role' in data else 'customer'
    now = datetime.datetime.now()
    con.execute(sql_add_user, (user_id, data['username'], data['email'], data['password'], role, now, now))
    user_id += 1

    return ({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    global session_id
    data = request.get_json()
    sql_select = 'SELECT * FROM user WHERE email=? and password_hash=?'
    person = con.execute(sql_select, (data['email'], data['password_hash']))
    person = person.fetchall()
    if person != []:
        data_session = dict()
        data_session['id'] = session_id
        print(person)
        data_session['user_id'] = person[0][0]
        session_id += 1
        encoded_jwt = jwt.encode(data_session, "secret", algorithm="HS256")
        data_session['session_token'] = encoded_jwt
        data_session['expires_at'] = datetime.datetime.now() + datetime.timedelta(minutes=2)
        return ({"message": "Login successful", "token": encoded_jwt}), 200
    else:
        return ({"message": "Invalid email or password", "token": None}), 401


@app.route('/token', methods=['POST'])
def loginToken():
    data = request.get_json()
    token = data['token']
    select_token = 'SELECT * FROM session WHERE session_token=?'
    check = con.execute(select_token, (token))
    return check.fetchall() != []


@app.route('/user_info', methods=['GET'])
def user_info():
    data = request.get_json()
    user_select = 'SELECT * FROM user WHERE id=?'
    select_token = 'SELECT * FROM session WHERE session_token=?'
    id_user = con.execute(select_token, (data['token'])).fetchall()[0][1]
    person_inf = con.execute(user_select, (id_user)).fetchall()
    return {'username': person_inf[1], 'email': person_inf[2], 'role': person_inf[4]}

if __name__ == "__main__":
    app.run(debug=True, port=3009)
