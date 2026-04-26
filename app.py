from flask import Flask, render_template, request, redirect, session
import random
import os
from datetime import date
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "secretkey123"

# -------------------------------
# ENCRYPTION KEY
# -------------------------------
key = b'e4_wkUSBAzcbGqPQB7cdJKqH1uo3o8goo-iE-1JFW1k='
cipher = Fernet(key)

# -------------------------------
# STUDENTS DATA
# -------------------------------
students = {
    "11239A066": "2006-07-20",
    "11239A103": "2005-05-27",
    "11239A052": "2005-09-02"
}

# -------------------------------
# TEACHER LOGIN
# -------------------------------
admin_username = "admin"
admin_password = "1234"

# -------------------------------
# QUESTIONS
# -------------------------------
questions = [
    "Write a Python program to find factorial of a number",
    "Write a Python program to check prime number",
    "Write a Python program to reverse a string",
    "Write a Python program to add two numbers",
    "Write a Python program to check palindrome",
    "Write a Python program to print Fibonacci series"
]

current_questions = []

# -------------------------------
# HOME
# -------------------------------
@app.route('/')
def home():
    return render_template("login.html")

# -------------------------------
# STUDENT LOGIN
# -------------------------------
@app.route('/login', methods=['POST'])
def login():
    global current_questions

    regno = request.form['regno']
    dob = request.form['dob']

    if os.path.exists("answers_" + regno + ".txt"):
        return "You already submitted exam"

    if regno in students and students[regno] == dob:
        session['student'] = regno
        current_questions = random.sample(questions, 2)
        return redirect('/exam')
    else:
        return "Invalid Login"

# -------------------------------
# EXAM PAGE
# -------------------------------
@app.route('/exam')
def exam():

    if 'student' not in session:
        return redirect('/')

    return render_template(
        "exam.html",
        q1=current_questions[0],
        q2=current_questions[1],
        subject="PYTHON PROGRAMMING",
        code="BCSF186T20",
        year="2nd Year",
        semester="4th Semester",
        exam_date=str(date.today()),
        regno=session['student']
    )

# -------------------------------
# SUBMIT EXAM (ENCRYPTED)
# -------------------------------
@app.route('/submit', methods=['POST'])
def submit():

    if 'student' not in session:
        return redirect('/')

    ans1 = request.form['ans1']
    ans2 = request.form['ans2']
    reason = request.form['reason']
    copywarn = request.form.get('copywarn', "0")

    # 🔐 Encrypt answers
    enc_ans1 = cipher.encrypt(ans1.encode()).decode()
    enc_ans2 = cipher.encrypt(ans2.encode()).decode()

    filename = "answers_" + session['student'] + ".txt"

    with open(filename, "w") as f:

        f.write("Student: " + session['student'] + "\n\n")

        f.write("Subject: PYTHON PROGRAMMING\n")
        f.write("Subject Code: BCSF186T20\n")
        f.write("Year: 2nd Year\n")
        f.write("Semester: 4th Semester\n")
        f.write("Date: " + str(date.today()) + "\n\n")

        f.write("Question 1:\n")
        f.write(current_questions[0] + "\n")
        f.write("Answer:\n")
        f.write(enc_ans1 + "\n\n")

        f.write("Question 2:\n")
        f.write(current_questions[1] + "\n")
        f.write("Answer:\n")
        f.write(enc_ans2 + "\n\n")

        f.write("Submission Status:\n")
        f.write(reason + "\n\n")

        f.write("Copy Paste Warnings:\n")
        f.write(copywarn)

    session.pop('student', None)

    return "Exam Submitted Successfully"

# -------------------------------
# TEACHER LOGIN
# -------------------------------
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():

    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        if user == admin_username and pwd == admin_password:
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Invalid Teacher Login"

    return render_template("adminlogin.html")

# -------------------------------
# ADMIN PANEL
# -------------------------------
@app.route('/admin')
def admin():

    if not session.get('admin'):
        return redirect('/adminlogin')

    files = os.listdir()
    students_list = []

    for file in files:
        if file.startswith("answers_"):
            regno = file.replace("answers_", "").replace(".txt", "")
            students_list.append(regno)

    return render_template("admin.html", students=students_list)

# -------------------------------
# VIEW ANSWERS (DECRYPTED)
# -------------------------------
@app.route('/view/<regno>')
def view(regno):

    if not session.get('admin'):
        return redirect('/adminlogin')

    filename = "answers_" + regno + ".txt"

    if not os.path.exists(filename):
        return "No file found"

    with open(filename, "r") as f:
        lines = f.readlines()

    output = ""

    for line in lines:
        line = line.strip()
        try:
            decrypted = cipher.decrypt(line.encode()).decode()
            output += decrypted + "\n"
        except:
            output += line + "\n"

    return render_template("view.html", data=output)

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)