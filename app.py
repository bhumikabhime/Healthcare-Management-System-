import os
import csv
import io
import joblib
import numpy as np
from werkzeug.utils import secure_filename
import shutil 
from DL.predict import predict_xray
from flask import Flask, render_template, request, redirect, flash, session, send_file, Response
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.platypus import ( SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle )
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from config import create_tables, create_connection

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.secret_key = "AI_Doctor_Assistant_2026"

create_tables()

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM doctors WHERE email = ?",
            (email,)
        )

        doctor = cursor.fetchone()

        conn.close()

        if doctor:

            if check_password_hash(doctor["password"], password):

                session["doctor_name"] = doctor["fullname"]
                session["doctor_email"] = doctor["email"]
                session["profile_image"] = doctor["profile_image"]
                flash("Login Successful!", "success")

                return redirect("/dashboard")

        flash("Invalid Email or Password!", "danger")

    return render_template("login.html")


# ------------------------
# Register Page
# ------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        profile_image = request.files.get("profile_image")
        # default filename for new registrations
        filename = "default.png"

        # if the user uploaded an image, save it and use that filename
        if profile_image and profile_image.filename:
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join("static", "images", filename))
 
        # ensure form fields are read before use
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        conn = create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO doctors(fullname,email,password)
                VALUES(?,?,?)
                """,
                (fullname, email, hashed_password),
            )
            conn.commit()
            flash("Registration Successful! Please Login.", "success")
            return redirect("/")
        except Exception:
            flash("Email already exists!", "danger")
            return redirect("/register")
        finally:
            conn.close()

    return render_template("register.html")


# ------------------------
# Dashboard
# ------------------------
@app.route("/dashboard")
def dashboard():

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    conn = create_connection()
    cursor = conn.cursor()
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    date_filter = ""
    params = []

    if from_date and to_date:
     date_filter = " WHERE DATE(prediction_date) BETWEEN ? AND ? "
    params = [from_date, to_date]

    # Total Reports
    if date_filter:
     cursor.execute(
        f"SELECT COUNT(*) FROM prediction_history {date_filter}",
        params
    )
    else:
     cursor.execute("SELECT COUNT(*) FROM prediction_history")
    total_reports = cursor.fetchone()[0]

    # Total Unique Patients
    if date_filter:
     cursor.execute(f"""
        SELECT COUNT(DISTINCT patient_name)
        FROM prediction_history
        {date_filter}
    """, params)
    else:
     cursor.execute("""
        SELECT COUNT(DISTINCT patient_name)
        FROM prediction_history
    """)

    total_patients = cursor.fetchone()[0]
# -----------------------------
# Chest X-Ray Reports
# -----------------------------
    cursor.execute("""
    SELECT COUNT(*)
    FROM prediction_history
    WHERE prediction_model = 'Chest X-Ray'
""")
    chest_xray_reports = cursor.fetchone()[0]

# -----------------------------
# Diabetes Reports
# -----------------------------
    cursor.execute("""
    SELECT COUNT(*)
    FROM prediction_history
    WHERE prediction_model = 'Diabetes'
""")
    diabetes_reports = cursor.fetchone()[0]

# -----------------------------
# Breast Cancer Reports
# -----------------------------
    cursor.execute("""
    SELECT COUNT(*)
    FROM prediction_history
    WHERE prediction_model = 'Cancer'
""")
    breast_cancer_reports = cursor.fetchone()[0]

    # Recent Predictions (last 5)
    cursor.execute("""
        SELECT 
               patient_name,
               prediction_model,
               prediction,
               confidence,
               prediction_date
        FROM prediction_history
        ORDER BY prediction_date DESC
        LIMIT 5
    """)
    recent_predictions = cursor.fetchall()

    # Monthly Reports
    cursor.execute("""
        SELECT
            strftime('%m', prediction_date) AS month_number,
            CASE strftime('%m', prediction_date)
                WHEN '01' THEN 'Jan'
                WHEN '02' THEN 'Feb'
                WHEN '03' THEN 'Mar'
                WHEN '04' THEN 'Apr'
                WHEN '05' THEN 'May'
                WHEN '06' THEN 'Jun'
                WHEN '07' THEN 'Jul'
                WHEN '08' THEN 'Aug'
                WHEN '09' THEN 'Sep'
                WHEN '10' THEN 'Oct'
                WHEN '11' THEN 'Nov'
                WHEN '12' THEN 'Dec'
            END AS month,
            COUNT(*) AS total
        FROM prediction_history
        GROUP BY month_number
        ORDER BY month_number
    """)

    monthly_data = cursor.fetchall()
    months = [row["month"] for row in monthly_data]
    monthly_reports = [row["total"] for row in monthly_data]

    # Gender Distribution
    cursor.execute("""
        SELECT
            patient_gender,
            COUNT(*) AS total
        FROM prediction_history
        GROUP BY patient_gender
    """)

    gender_data = cursor.fetchall()

    male_count = 0
    female_count = 0

    for row in gender_data:
        gender = row["patient_gender"].lower()
        if gender == "male":
            male_count = row["total"]
        elif gender == "female":
            female_count = row["total"]

    # Last 7 Days Prediction Trend
    cursor.execute("""
        SELECT
            DATE(prediction_date) AS day,
            COUNT(*) AS total
        FROM prediction_history
        WHERE DATE(prediction_date) >= DATE('now', '-6 days')
        GROUP BY DATE(prediction_date)
        ORDER BY DATE(prediction_date)
    """)

    trend_data = cursor.fetchall()
    trend_days = [row["day"] for row in trend_data]
    trend_counts = [row["total"] for row in trend_data]

    conn.close()

    return render_template(
        "dashboard.html",
        total_reports=total_reports,
        total_patients=total_patients,
        chest_xray_reports=chest_xray_reports,
        diabetes_reports=diabetes_reports,
        breast_cancer_reports=breast_cancer_reports,
        recent_predictions=recent_predictions,
        months=months,
        monthly_reports=monthly_reports,
        male_count=male_count,
        female_count=female_count,
        trend_days=trend_days,
        trend_counts=trend_counts,
        from_date=from_date,
        to_date=to_date,
    )

# ------------------------
# Chest X-Ray
# ------------------------
@app.route("/chest-xray", methods=["GET", "POST"])
def chest_xray():

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    prediction = None
    confidence = None
    image_path = None

    if request.method == "POST":

        if "xray_image" not in request.files:
            flash("Please select an image.", "danger")
            return redirect("/chest-xray")

        file = request.files["xray_image"]

        if file.filename == "":
            flash("Please select an image.", "danger")
            return redirect("/chest-xray")

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(filepath)

        prediction, confidence = predict_xray(filepath)

        # Patient Details
        patient_name = request.form["patient_name"]
        patient_age = request.form["patient_age"]
        patient_gender = request.form["patient_gender"]

        # Save to Database
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO prediction_history(
                doctor_name,
                doctor_email,
                patient_name,
                patient_age,
                patient_gender,
                image_name,
                prediction,
                confidence,
                prediction_model
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["doctor_name"],
            session["doctor_email"],
            patient_name,
            patient_age,
            patient_gender,
            filename,
            prediction,
            confidence,
            "Chest X-Ray"
        ))

        conn.commit()
        conn.close()

        image_path = filepath

    return render_template(
        "chest_xray.html",
        prediction=prediction,
        confidence=confidence,
        image_path=image_path
    )

# prediction_history
@app.route("/prediction-history")
def prediction_history():

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    search = request.args.get("search", "")

    conn = create_connection()
    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT *
            FROM prediction_history
            WHERE patient_name LIKE ?
            ORDER BY prediction_date DESC
        """, (f"%{search}%",))

    else:

        cursor.execute("""
            SELECT *
            FROM prediction_history
            ORDER BY prediction_date DESC
        """)

    history = cursor.fetchall()

    conn.close()

    return render_template(
        "prediction_history.html",
        history=history,
        search=search
    )
# Add the Export CSV route
@app.route("/export-csv")
def export_csv():

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            patient_name,
            patient_age,
            patient_gender,
            prediction,
            confidence,
            doctor_name,
            prediction_date
        FROM prediction_history
        ORDER BY prediction_date DESC
    """)

    records = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Patient Name",
        "Age",
        "Gender",
        "Prediction",
        "Confidence (%)",
        "Doctor",
        "Prediction Date"
    ])

    for row in records:
        writer.writerow([
            row["patient_name"],
            row["patient_age"],
            row["patient_gender"],
            row["prediction"],
            row["confidence"],
            row["doctor_name"],
            row["prediction_date"]
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=prediction_history.csv"
        }
    )
# ADD THIS NEW ROUTE HERE
@app.route("/delete-history/<int:id>")
def delete_history(id):

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM prediction_history WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Prediction deleted successfully!", "success")

    return redirect("/prediction-history")

 # PASTE THE download_report() ROUTE HERE

@app.route("/download-report/<int:id>")
def download_report(id):

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM prediction_history
        WHERE id = ?
    """, (id,))

    report = cursor.fetchone()

    conn.close()

    if report is None:
        flash("Report not found!", "danger")
        return redirect("/prediction-history")

    pdf_filename = f"Report_{id}.pdf"

    doc = SimpleDocTemplate(pdf_filename)
    styles = getSampleStyleSheet()

    elements = []

    logo_path = "static/logo/hospital_logo.png"

    logo = Image(logo_path, width=120, height=120)

    elements.append(logo)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>AI Doctor Assistant</b>", styles["Title"]))

    if report["prediction_model"] == "Chest X-Ray":
     report_title = "Chest X-Ray Diagnostic Report"

    elif report["prediction_model"] == "Diabetes":
     report_title = "Diabetes Diagnostic Report"

    elif report["prediction_model"] == "Cancer":
     report_title = "Breast Cancer Diagnostic Report"
 
    else:
     report_title = "Medical Diagnostic Report"

    elements.append(Paragraph(report_title, styles["Heading2"]))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b>Doctor:</b> {report['doctor_name']}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    patient_data = [
        ["Patient Name", report["patient_name"]],
        ["Age", str(report["patient_age"])],
        ["Gender", report["patient_gender"]],
        ["Prediction Date", str(report["prediction_date"])],
    ]

    table = Table(patient_data, colWidths=[2.2*inch, 3.8*inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),

        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),

        ('BACKGROUND', (1, 0), (1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

# ----------------------------
# X-Ray Image (Only for Chest X-Ray)
# ----------------------------
    if report["prediction_model"] == "Chest X-Ray":

        image_path = os.path.join(
            "static",
            "uploads",
            report["image_name"]
        )

        if os.path.exists(image_path):

            elements.append(Spacer(1, 15))
            elements.append(
                Paragraph("<b>Chest X-Ray Image</b>", styles["Heading2"])
            )
            elements.append(Spacer(1, 10))

            xray = Image(image_path, width=250, height=250)
            elements.append(xray)

            elements.append(Spacer(1, 20))
    # ----------------------------
# Prediction Details
# ----------------------------
    elements.append(
    Paragraph(f"<b>Prediction:</b> {report['prediction']}", styles["Normal"])
)

    elements.append(
    Paragraph(f"<b>Confidence:</b> {report['confidence']}%", styles["Normal"])
)

    elements.append(
    Paragraph(f"<b>Date:</b> {report['prediction_date']}", styles["Normal"])
)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Medical Recommendation</b>", styles["Heading2"]))

# -----------------------------------
# Recommendation Based on AI Model
# -----------------------------------

    if report["prediction_model"] == "Chest X-Ray":
        if report["prediction"] == "PNEUMONIA":
            recommendation = """
            • Signs of pneumonia are detected by the AI model.<br/>
            • Please consult a pulmonologist or physician as soon as possible.<br/>
            • Follow prescribed medications and treatment.<br/>
            • Seek immediate medical attention if breathing becomes difficult.
            """
        else:
            recommendation = """
            • No signs of pneumonia were detected by the AI model.<br/>
            • Continue maintaining good respiratory health.<br/>
            • If symptoms such as fever, cough, or chest pain persist, consult a healthcare professional.
            """

    elif report["prediction_model"] == "Diabetes":
        if report["prediction"] == "Diabetic":
            recommendation = """
            • The AI model indicates a high likelihood of diabetes.<br/>
            • Please consult a physician or endocrinologist.<br/>
            • Monitor your blood glucose regularly.<br/>
            • Maintain a healthy diet and exercise routine.
            """
        else:
            recommendation = """
            • The AI model indicates no evidence of diabetes.<br/>
            • Continue maintaining a healthy lifestyle.<br/>
            • Schedule routine health check-ups.
            """

    elif report["prediction_model"] == "Cancer":

     if report["prediction"] == "Malignant":

        recommendation = """
        • The AI model predicts a high likelihood of malignant breast cancer.<br/>
        • Please consult an oncologist or breast cancer specialist immediately.<br/>
        • Additional diagnostic tests such as biopsy, mammography, or MRI may be required.<br/>
        • Early diagnosis and treatment significantly improve outcomes.
        """

     else:

        recommendation = """
        • The AI model predicts the tumor is likely benign.<br/>
        • Continue regular breast examinations and routine screening.<br/>
        • Follow your physician's advice for periodic monitoring.<br/>
        • Consult a healthcare professional if any new symptoms appear.
        """

    else:

     recommendation = """
    • Please consult your physician for further evaluation.
    """

    elements.append(Paragraph(recommendation, styles["Normal"]))

    elements.append(Spacer(1, 30))
    elements.append(Paragraph("<b>Doctor's Signature</b>", styles["Normal"]))
    elements.append(Paragraph("______________________________", styles["Normal"]))

    doc.build(elements)

    return send_file(pdf_filename, as_attachment=True)

# ------------------------
# Diabetes
# ------------------------
@app.route("/diabetes", methods=["GET", "POST"])
def diabetes():

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    prediction = None
    confidence = None

    if request.method == "POST":

        # Load Model
        model = joblib.load("models/diabetes.pkl")

        # Patient Details
        patient_name = request.form["patient_name"]
        patient_gender = request.form["patient_gender"]
        patient_age = request.form["Age"]

        # Diabetes Features
        features = np.array([[
            float(request.form["Pregnancies"]),
            float(request.form["Glucose"]),
            float(request.form["BloodPressure"]),
            float(request.form["SkinThickness"]),
            float(request.form["Insulin"]),
            float(request.form["BMI"]),
            float(request.form["DiabetesPedigreeFunction"]),
            float(request.form["Age"])
        ]])

        # Prediction
        result = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        confidence = round(max(probability) * 100, 2)

        if result == 1:
            prediction = "Diabetic"
        else:
            prediction = "Non-Diabetic"

        # Save to Database
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO prediction_history(
                doctor_name,
                doctor_email,
                patient_name,
                patient_age,
                patient_gender,
                image_name,
                prediction,
                confidence,
                prediction_model
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["doctor_name"],
            session["doctor_email"],
            patient_name,
            patient_age,
            patient_gender,
            "diabetes",
            prediction,
            confidence,
            "Diabetes"
        ))

        conn.commit()
        conn.close()

    return render_template(
        "diabetes.html",
        prediction=prediction,
        confidence=confidence
    )

# ------------------------
# Cancer
# ------------------------
@app.route("/cancer", methods=["GET", "POST"])
def cancer():

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    prediction = None
    confidence = None

    if request.method == "POST":

        # Load Model
        model = joblib.load("models/cancer.pkl")

        # -----------------------------
        # Patient Details
        # -----------------------------
        patient_name = request.form["patient_name"]
        patient_age = request.form["patient_age"]
        patient_gender = request.form["patient_gender"]

        # -----------------------------
        # Cancer Features
        # -----------------------------
        features = np.array([[
            float(request.form["radius_mean"]),
            float(request.form["texture_mean"]),
            float(request.form["perimeter_mean"]),
            float(request.form["area_mean"]),
            float(request.form["smoothness_mean"]),
            float(request.form["compactness_mean"]),
            float(request.form["concavity_mean"]),
            float(request.form["concave_points_mean"]),
            float(request.form["symmetry_mean"]),
            float(request.form["fractal_dimension_mean"]),

            float(request.form["radius_se"]),
            float(request.form["texture_se"]),
            float(request.form["perimeter_se"]),
            float(request.form["area_se"]),
            float(request.form["smoothness_se"]),
            float(request.form["compactness_se"]),
            float(request.form["concavity_se"]),
            float(request.form["concave_points_se"]),
            float(request.form["symmetry_se"]),
            float(request.form["fractal_dimension_se"]),

            float(request.form["radius_worst"]),
            float(request.form["texture_worst"]),
            float(request.form["perimeter_worst"]),
            float(request.form["area_worst"]),
            float(request.form["smoothness_worst"]),
            float(request.form["compactness_worst"]),
            float(request.form["concavity_worst"]),
            float(request.form["concave_points_worst"]),
            float(request.form["symmetry_worst"]),
            float(request.form["fractal_dimension_worst"])
        ]])

        # -----------------------------
        # Prediction
        # -----------------------------
        result = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        confidence = round(max(probability) * 100, 2)

        if result == 1:
            prediction = "Malignant"
        else:
            prediction = "Benign"

        # -----------------------------
        # Save to Database
        # -----------------------------
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO prediction_history(
                doctor_name,
                doctor_email,
                patient_name,
                patient_age,
                patient_gender,
                image_name,
                prediction,
                confidence,
                prediction_model
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["doctor_name"],
            session["doctor_email"],
            patient_name,
            patient_age,
            patient_gender,
            "cancer",
            prediction,
            confidence,
            "Cancer"
        ))

        conn.commit()
        conn.close()

    return render_template(
        "cancer.html",
        prediction=prediction,
        confidence=confidence
    )

# ------------------------
# Disease Prediction
# ------------------------
@app.route("/disease")
def disease():

    if "doctor_name" not in session:

        flash("Please login first.", "warning")
        return redirect("/")

    return render_template("disease.html")
# ------------------------
# Doctor Profile
# ------------------------
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "doctor_name" not in session:
        flash("Please login first.", "warning")
        return redirect("/")

    conn = create_connection()
    cursor = conn.cursor()

    # Get current doctor
    cursor.execute(
        "SELECT * FROM doctors WHERE email = ?",
        (session["doctor_email"],)
    )

    doctor = cursor.fetchone()

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]

        profile_image = request.files.get("profile_image")

        filename = doctor["profile_image"]

        if profile_image and profile_image.filename != "":

            filename = secure_filename(profile_image.filename)

            profile_image.save(
                os.path.join(
                    "static",
                    "images",
                    filename
                )
            )

        cursor.execute("""
            UPDATE doctors
            SET
                fullname = ?,
                email = ?,
                profile_image = ?
            WHERE email = ?
        """, (
            fullname,
            email,
            filename,
            session["doctor_email"]
        ))

        conn.commit()

        # Update session
        session["doctor_name"] = fullname
        session["doctor_email"] = email
        session["profile_image"] = filename

        flash("Profile updated successfully!", "success")

        # Reload doctor information
        cursor.execute(
            "SELECT * FROM doctors WHERE email = ?",
            (email,)
        )

        doctor = cursor.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        doctor=doctor
    )

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!", "success")

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
