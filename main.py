from flask import Flask, render_template, redirect, url_for, request, make_response, session, flash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from forms import ContactForm
import sqlite3 as sql
import os
import pathlib




app = Flask(__name__)
app.secret_key = 'dvuie89hh92fg9bf39fvsdj'

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name


@app.route('/score/<int:score>')
def hello_score(score):
    return render_template('score.html', marks=score)


@app.route('/result')
def result():
    dict = {'phy':50,'che':60,'maths':70}
    return render_template('result.html', result = dict)


@app.route("/staticfield")
def staticfield():
   return render_template("staticfield.html")


@app.route('/student')
def student():
    return render_template('student.html')


@app.route('/student_result',methods = ['POST', 'GET'])
def student_result():
    if request.method == 'POST':
        res = request.form
        return render_template("student_result.html",result = res)

@app.route('/hello/<user>')
def hello_name(user):
    return render_template('hello.html', name=user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('success', name=user))
    else:
        return render_template("login.html")


@app.route('/cookie')
def cookie():
   return render_template('cookie.html')


@app.route('/setcookie', methods=['POST', 'GET'])
def setcookie():
    if request.method == 'POST':
        user = request.form['nm']

    resp = make_response(render_template('readcookie.html'))
    resp.set_cookie('userID', user)

    return resp

@app.route('/getcookie')
def getcookie():
   name = request.cookies.get('userID')
   return '<h1>welcome '+name+'</h1>'




# SESSIONS
@app.route('/visits_counter/')
def visits():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1  # reading and updating session data
    else:
        session['visits'] = 1 # setting session data
    return "Total visits: {}".format(session.get('visits'))

@app.route('/delete_visits/')
def delete_visits():
    session.pop('visits', None) # delete visits
    return 'Visits deleted'



# FILE UPLOADS

UPLOAD_FOLDER = './static/files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload')
def upload_file():
    return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploader', methods=['GET', 'POST'])
def uploader_init():
    if request.method == 'POST':
        f = request.files['file']

        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            pathlib.Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(file_path)
            f.save(file_path)
            return 'file uploaded successfully'
        else:
            return 'file can\'t be uploaded!'


# SENDING MAILS
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'bdudapythontest1234@gmail.com'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True



@app.route("/sendmailform")
def sendmailform():
    return render_template("sendmailform.html")

@app.route("/sendmail", methods=['POST', 'GET'])
def sendmail():
    app.logger.info("SEND MAIL START")
    if request.method == 'POST':
        mail_pass = request.form['mail_password']
        mail_to = request.form['mail_to']
        mail_text = request.form['mail_text']
        mail_from = app.config['MAIL_USERNAME']
        app.config['MAIL_PASSWORD'] = mail_pass
        print(mail_pass)
        mail = Mail(app)


        msg = Message('Hello', sender = mail_from, recipients = [mail_to])
        msg.body = mail_text
        try:
            mail.send(msg)
            return "Mail sent successfully!"
        except:
            return "Username and password not accepted!"

    else:
        return "MAIL NOT SENT"



# WTForms
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
            return render_template('success.html')
    elif request.method == 'GET':
        return render_template('contact.html', form=form)




# SQLite

@app.route('/enternew')
def new_student():
    return render_template('student_sql.html')


@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            nm = request.form['nm']
            addr = request.form['add']
            city = request.form['city']
            pin = request.form['pin']

            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("INSERT INTO students (name,addr,city,pin) VALUES(?, ?, ?, ?)",(nm,addr,city,pin) )

                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("student_sql_result.html", msg=msg)
            con.close()


@app.route('/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from students")

    rows = cur.fetchall();
    return render_template("student_sql_list.html", rows=rows)





if __name__ == "__main__":
    print("FLASK TP APP - MAIN START")
    app.debug = False
    app.run()




