from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

config = {
  "apiKey": "AIzaSyAW0fPhTgARgfO5MOnLpQrvOLmXib2_xcE",
  'authDomain': "email-e597f.firebaseapp.com",
  'projectId': "email-e597f",
  'storageBucket': "email-e597f.appspot.com",
  'messagingSenderId': "800894584401",
  'appId': "1:800894584401:web:87a738b13e841b095f5a70",
  'measurementId': "G-7X385Z0KYJ",
  "databaseURL": "https://email-e597f-default-rtdb.europe-west1.firebasedatabase.app/"

}

firebase = pyrebase.initialize_app(config)
auth=firebase.auth()
db =firebase.database()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

#Code goes below here
@app.route('/',methods=['GET','POST'])
def signin():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['Password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            
            return redirect(url_for('inbox'))
        except Exception as e:
            error = "Authentication failed"
            print(e)
    return render_template("signin.html")
@app.route('/signup', methods=['GET', 'POST'])
def signup(): 
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['Password']
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            user={'email':email}
            db.child('Users').child(UID).set(user)
            return redirect(url_for('inbox'))
        except:
            error = "Authentication failed"
            return redirect(url_for('signup'))
    else:
        return render_template("signup.html")
    
def fetch_user_messages(uid):
    messages = db.child("Users").child(uid).child('message').get().val()
    user_messages = []
    if messages:
        for message_id, message_data in messages.items():
            sender_uid = message_data['sender']
            sender_email = db.child("Users").child(sender_uid).child('email').get().val()
            message_data['sender_email'] = sender_email
            user_messages.append(message_data)
    return user_messages

    

@app.route('/inbox', methods=['GET', 'POST'])
def inbox():
    if request.method == 'POST':
        return render_template('compose.html')
    else:
        UID = login_session['user']['localId']
        user_messages = fetch_user_messages(UID)
        return render_template('inbox.html', messages=user_messages)


# Your routes and other code above

def email_to_uid(to):
    users = db.child("Users").get().val()
    for uid, user_data in users.items():
        if user_data['email'] == to:
            return uid
    return None

@app.route('/compose', methods=['GET', 'POST'])
def compose():
    if request.method == 'POST':
        rec = request.form['email']
        subject = request.form['subject']
        body = request.form['body']
        sender_uid = login_session['user']['localId']
        recipient_uid = email_to_uid(rec)

        if recipient_uid is None:
            flash("Recipient email not found.")
            return redirect('compose')

        letter = {'sender': sender_uid, 'to': rec, "subject": subject, "body": body}
        try:
            db.child("Users").child(recipient_uid).child('message').push(letter)
            
            return redirect(url_for("inbox"),letter)
        except Exception as e:
            print(e)
            return redirect('compose')
    else:

        return render_template('compose.html')

# ... (your other routes and code)

if __name__ == '__main__':
    app.run(debug=True)

#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)