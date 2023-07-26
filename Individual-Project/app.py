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
@app.route('/inbox', methods=['GET','POST'])
def inbox():
    if request.method=='POST':
        return render_template('compose.html')
    else:
        return render_template('inbox.html')
# def email_to_uid(to):
#     users=[db.child("Users").get().val()]
#     for user in users:
#         if users[user]['email']==to:
#             return user
#     return None
    
    
# @app.route('/compose',methods=['GET','POST'])
# def compsoe():
#     if request.method=='POST':
#          rec=request.form['email']
#          subject=request.form['subject']
#          body=request.form['body']
#          UID = login_session['user']['localId']
#          letter={'sender':UID,'to':rec,"subject":subject,"body":body}
#          try:
#             # db.child("Messages").push(letter)
#             db.child("Users").child(email_to_uid(letter['to'])).push(letter)
#             return render_template("inbox.html")
#          except:
#              return redirect('compose')
#     else:
#         return render_template('compose.html')
# ... (your imports and Firebase configuration code)

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
            db.child("Users").child(recipient_uid).child('email').child('message').push(letter)
            return redirect(url_for("inbox"))
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