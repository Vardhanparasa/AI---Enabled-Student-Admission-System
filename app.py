import joblib
import pandas as pd
import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "AI_Admission_System_2026"

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- STUDENT ---------------- #

@app.route("/student-login")
def student_login():
    return render_template("student_login.html")


@app.route("/student-register")
def student_register():
    return render_template("student_register.html")


@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("admission.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO students(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )
        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return """
        <h2>Email already registered!</h2>
        <br>
        <a href='/student-register'>Try Again</a>
        """

    conn.close()

    return """
    <h2>Registration Successful ✅</h2>
    <br>
    <a href='/student-login'>Login Now</a>
    """


@app.route("/student-dashboard", methods=["POST"])
def student_dashboard():

    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("admission.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE email=? AND password=?",
        (email, password)
    )

    student = cursor.fetchone()

    conn.close()

    if student:

        session["student_id"] = student[0]
        session["student_name"] = student[1]
        session["student_email"] = student[2]

        conn = sqlite3.connect("admission.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM applications WHERE student_email=?",
            (student[2],)
        )

        application = cursor.fetchone()

        conn.close()

        if application:
            return redirect("/student-status")
        else:
            return redirect("/admission-form")

    else:

        return """
        <h2 style='color:red;'>Invalid Email or Password ❌</h2>

        <br>

        <a href='/student-login'>Try Again</a>
        """

@app.route("/student-status")
def student_status():

    student_email = session["student_email"]

    conn = sqlite3.connect("admission.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ai_prediction, final_status
        FROM applications
        WHERE student_email=?
        ORDER BY application_id DESC
        LIMIT 1
    """, (student_email,))

    result = cursor.fetchone()

    conn.close()

    if result:

        return f"""
        <h1>Application Status</h1>

        <h2>AI Recommendation : {result[0]}</h2>

        <h2>Final Status : {result[1]}</h2>

        <br>

        <a href='/'>Home</a>
        """

    else:

        return """
        <h2>No Application Found</h2>

        <a href='/'>Home</a>
        """

# ---------------- ADMISSION FORM ---------------- #

@app.route("/admission-form")
def admission_form():
    return render_template("admission_form.html")


@app.route("/submit-application", methods=["POST"])
def submit_application():

    # Logged-in Student
    student_id = session["student_id"]
    student_name = session["student_name"]
    student_email = session["student_email"]

    # Form Data
    age = int(request.form["age"])
    gender = request.form["gender"].lower()
    category = request.form["category"].lower()
    state = request.form["state"].lower()
    preferred_stream = request.form["preferred_stream"].lower()
    entrance_exam = request.form["entrance_exam"].lower()
    entrance_score = int(request.form["entrance_score"])
    board_percentage = float(request.form["board_percentage"])
    extracurricular_score = int(request.form["extracurricular_score"])
    scholarship_eligibility = request.form["scholarship_eligibility"].lower()

    # Load AI Model & Encoders
    model = joblib.load("admission_model.pkl")
    encoders = joblib.load("encoders.pkl")

    # Encode Categorical Values
    gender = encoders["gender"].transform([gender])[0]
    category = encoders["category"].transform([category])[0]
    state = encoders["state"].transform([state])[0]
    preferred_stream = encoders["preferred_stream"].transform([preferred_stream])[0]
    entrance_exam = encoders["entrance_exam"].transform([entrance_exam])[0]
    scholarship_eligibility = encoders["scholarship_eligibility"].transform([scholarship_eligibility])[0]

    # Prepare Data
    data = pd.DataFrame([{
        "age": age,
        "gender": gender,
        "category": category,
        "state": state,
        "preferred_stream": preferred_stream,
        "entrance_exam": entrance_exam,
        "entrance_score": entrance_score,
        "board_percentage": board_percentage,
        "extracurricular_score": extracurricular_score,
        "scholarship_eligibility": scholarship_eligibility
    }])

    # AI Prediction
    prediction = model.predict(data)[0]

    if prediction == 0:
        ai_prediction = "Admitted"
    else:
        ai_prediction = "Rejected"

    # Save to Database
    conn = sqlite3.connect("admission.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO applications(
            student_id,
            student_name,
            student_email,
            age,
            gender,
            category,
            state,
            preferred_stream,
            entrance_exam,
            entrance_score,
            board_percentage,
            extracurricular_score,
            scholarship_eligibility,
            ai_prediction,
            final_status
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        student_id,
        student_name,
        student_email,
        age,
        request.form["gender"],
        request.form["category"],
        request.form["state"],
        request.form["preferred_stream"],
        request.form["entrance_exam"],
        entrance_score,
        board_percentage,
        extracurricular_score,
        request.form["scholarship_eligibility"],
        ai_prediction,
        "Pending"
    ))

    conn.commit()
    conn.close()

    return f"""
    <h2>🎉 Application Submitted Successfully</h2>

    <h3>Student : {student_name}</h3>

    <h3>AI Recommendation : {ai_prediction}</h3>

    <h3>Final Status : Pending</h3>

    <br>

    <a href="/">Go to Home</a>
    """


# ---------------- ADMIN ---------------- #

@app.route("/admin-login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin-dashboard", methods=["POST"])
def admin_dashboard():

    username = request.form["username"]
    password = request.form["password"]

    admin_username = "admin@gmail.com"
    admin_password = "abcdefghij"

    if username == admin_username and password == admin_password:

        return """
        <h2>Welcome Admin ✅</h2>

        <br>

        <a href='/view-applications'>View Student Applications</a>
        """

    else:

        return """
        <h2 style='color:red;'>Invalid Admin Credentials ❌</h2>

        <br>

        <a href='/admin-login'>Try Again</a>
        """


@app.route("/view-applications")
def view_applications():

    conn = sqlite3.connect("admission.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications")

    applications = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        applications=applications
    )

@app.route("/approve/<int:id>")
def approve(id):

    conn = sqlite3.connect("admission.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE applications SET final_status='Approved' WHERE application_id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view-applications")


@app.route("/reject/<int:id>")
def reject(id):

    conn = sqlite3.connect("admission.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE applications SET final_status='Rejected' WHERE application_id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view-applications")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)