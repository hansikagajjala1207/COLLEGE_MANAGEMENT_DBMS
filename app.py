"""
====================================================================
DESIGN AND IMPLEMENTATION OF A DATABASE MANAGEMENT SYSTEM
FOR STUDENT AND COLLEGE MANAGEMENT SYSTEM
Academic Project: 2nd Year B.Tech DBMS Assignment
Full-Stack Flask + MySQL 8 Web Application
====================================================================
"""

import functools
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import mysql.connector
from config import Config
import db

app = Flask(__name__)
app.config.from_object(Config)


# ====================================================================
# AUTHENTICATION & ROUTE GUARDS
# ====================================================================

def login_required(view):
    """Decorator to restrict access to authenticated administrators only."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please sign in with admin credentials to access this portal.", "warning")
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login handler with secure password verification."""
    # If already logged in, redirect straight to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('login.html')

        try:
            # Query user from MySQL database
            user = db.query_one(
                "SELECT user_id, username, password_hash, full_name, role FROM users WHERE username = %s",
                (username,)
            )

            if user and check_password_hash(user['password_hash'], password):
                session.clear()
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                flash(f"Welcome back, {user['full_name']}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password. Please try again.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Connection Error: {err.msg}. Ensure MySQL is running.", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Log out current user and clear session."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('login'))


# ====================================================================
# MODULE 2: DASHBOARD
# ====================================================================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard overview with 4 SQL COUNT cards and recent students."""
    try:
        # SQL COUNT queries for metrics
        student_count_row = db.query_one("SELECT COUNT(*) AS cnt FROM students")
        total_students = student_count_row['cnt'] if student_count_row else 0

        faculty_count_row = db.query_one("SELECT COUNT(*) AS cnt FROM faculty")
        total_faculty = faculty_count_row['cnt'] if faculty_count_row else 0

        dept_count_row = db.query_one("SELECT COUNT(*) AS cnt FROM departments")
        total_departments = dept_count_row['cnt'] if dept_count_row else 0

        course_count_row = db.query_one("SELECT COUNT(*) AS cnt FROM courses")
        total_courses = course_count_row['cnt'] if course_count_row else 0

        # Small table of recently added students (using INNER JOIN)
        recent_students = db.query_all(
            """SELECT s.student_id, s.roll_number, s.full_name, s.email, s.gender, s.admission_year,
                      d.dept_name, d.dept_code
               FROM students s
               INNER JOIN departments d ON s.dept_id = d.dept_id
               ORDER BY s.student_id DESC
               LIMIT 5"""
        )

        return render_template(
            'dashboard.html',
            active_page='dashboard',
            total_students=total_students,
            total_faculty=total_faculty,
            total_departments=total_departments,
            total_courses=total_courses,
            recent_students=recent_students
        )
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return render_template(
            'dashboard.html',
            active_page='dashboard',
            total_students=0,
            total_faculty=0,
            total_departments=0,
            total_courses=0,
            recent_students=[]
        )


# ====================================================================
# MODULE 3: STUDENT MANAGEMENT (Add, View, Edit, Delete, Search)
# ====================================================================

@app.route('/students')
@login_required
def students():
    """List students with search filter by Roll Number or Full Name."""
    search_query = request.args.get('search', '').strip()

    try:
        if search_query:
            sql = """SELECT s.*, d.dept_name, d.dept_code
                     FROM students s
                     INNER JOIN departments d ON s.dept_id = d.dept_id
                     WHERE s.roll_number LIKE %s OR s.full_name LIKE %s
                     ORDER BY s.student_id DESC"""
            wildcard = f"%{search_query}%"
            students_list = db.query_all(sql, (wildcard, wildcard))
        else:
            sql = """SELECT s.*, d.dept_name, d.dept_code
                     FROM students s
                     INNER JOIN departments d ON s.dept_id = d.dept_id
                     ORDER BY s.student_id DESC"""
            students_list = db.query_all(sql)

        return render_template(
            'students.html',
            active_page='students',
            students=students_list,
            search_query=search_query
        )
    except mysql.connector.Error as err:
        flash(f"Error fetching students: {err.msg}", "danger")
        return render_template('students.html', active_page='students', students=[], search_query=search_query)


@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Insert a new student into MySQL."""
    try:
        departments = db.query_all("SELECT dept_id, dept_name, dept_code FROM departments ORDER BY dept_name ASC")
    except mysql.connector.Error as err:
        flash(f"Error fetching departments: {err.msg}", "danger")
        departments = []

    if request.method == 'POST':
        roll_number = request.form.get('roll_number', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip() or None
        dob = request.form.get('dob', '').strip()
        gender = request.form.get('gender', '').strip()
        dept_id = request.form.get('dept_id', '').strip()
        admission_year = request.form.get('admission_year', '').strip()

        # Server-side validation
        if not (roll_number and full_name and email and dob and gender and dept_id and admission_year):
            flash("All required fields (*) must be completed.", "danger")
            return render_template('student_form.html', active_page='students', action='Add', departments=departments)

        try:
            insert_sql = """INSERT INTO students 
                            (roll_number, full_name, email, phone, dob, gender, dept_id, admission_year)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            db.execute_query(insert_sql, (roll_number, full_name, email, phone, dob, gender, dept_id, admission_year))
            flash(f"Student '{full_name}' ({roll_number}) successfully added!", "success")
            return redirect(url_for('students'))
        except mysql.connector.IntegrityError as err:
            if "Duplicate entry" in err.msg:
                flash(f"Duplicate Error: Roll number or Email already exists in the system.", "danger")
            else:
                flash(f"Integrity Error: {err.msg}", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('student_form.html', active_page='students', action='Add', departments=departments, student=None)


@app.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit and update an existing student record."""
    try:
        student = db.query_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
        departments = db.query_all("SELECT dept_id, dept_name, dept_code FROM departments ORDER BY dept_name ASC")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return redirect(url_for('students'))

    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for('students'))

    if request.method == 'POST':
        roll_number = request.form.get('roll_number', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip() or None
        dob = request.form.get('dob', '').strip()
        gender = request.form.get('gender', '').strip()
        dept_id = request.form.get('dept_id', '').strip()
        admission_year = request.form.get('admission_year', '').strip()

        try:
            update_sql = """UPDATE students 
                            SET roll_number = %s, full_name = %s, email = %s, phone = %s,
                                dob = %s, gender = %s, dept_id = %s, admission_year = %s
                            WHERE student_id = %s"""
            db.execute_query(update_sql, (roll_number, full_name, email, phone, dob, gender, dept_id, admission_year, student_id))
            flash(f"Student '{full_name}' successfully updated!", "success")
            return redirect(url_for('students'))
        except mysql.connector.IntegrityError as err:
            flash(f"Update Failed: Roll number or Email already in use by another student.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('student_form.html', active_page='students', action='Edit', departments=departments, student=student)


@app.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    """Safely delete a student from MySQL."""
    try:
        db.execute_query("DELETE FROM students WHERE student_id = %s", (student_id,))
        flash("Student record deleted successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Unable to delete student: {err.msg}", "danger")
    return redirect(url_for('students'))


# ====================================================================
# MODULE 4: FACULTY MANAGEMENT (Add, View, Edit, Delete, Search)
# ====================================================================

@app.route('/faculty')
@login_required
def faculty():
    """List faculty members with optional search by Name or Email."""
    search_query = request.args.get('search', '').strip()

    try:
        if search_query:
            sql = """SELECT f.*, d.dept_name, d.dept_code
                     FROM faculty f
                     INNER JOIN departments d ON f.dept_id = d.dept_id
                     WHERE f.faculty_name LIKE %s OR f.email LIKE %s
                     ORDER BY f.faculty_id DESC"""
            wildcard = f"%{search_query}%"
            faculty_list = db.query_all(sql, (wildcard, wildcard))
        else:
            sql = """SELECT f.*, d.dept_name, d.dept_code
                     FROM faculty f
                     INNER JOIN departments d ON f.dept_id = d.dept_id
                     ORDER BY f.faculty_id DESC"""
            faculty_list = db.query_all(sql)

        return render_template(
            'faculty.html',
            active_page='faculty',
            faculty_list=faculty_list,
            search_query=search_query
        )
    except mysql.connector.Error as err:
        flash(f"Error fetching faculty: {err.msg}", "danger")
        return render_template('faculty.html', active_page='faculty', faculty_list=[], search_query=search_query)


@app.route('/faculty/add', methods=['GET', 'POST'])
@login_required
def add_faculty():
    """Add a new faculty member with department foreign key association."""
    try:
        departments = db.query_all("SELECT dept_id, dept_name, dept_code FROM departments ORDER BY dept_name ASC")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        departments = []

    if request.method == 'POST':
        faculty_name = request.form.get('faculty_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip() or None
        dept_id = request.form.get('dept_id', '').strip()

        if not (faculty_name and email and dept_id):
            flash("Faculty Name, Email, and Department are required.", "danger")
            return render_template('faculty_form.html', active_page='faculty', action='Add', departments=departments)

        try:
            sql = "INSERT INTO faculty (faculty_name, email, phone, dept_id) VALUES (%s, %s, %s, %s)"
            db.execute_query(sql, (faculty_name, email, phone, dept_id))
            flash(f"Faculty member '{faculty_name}' added successfully!", "success")
            return redirect(url_for('faculty'))
        except mysql.connector.IntegrityError as err:
            flash(f"Error: Email address '{email}' is already registered.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('faculty_form.html', active_page='faculty', action='Add', departments=departments, faculty_member=None)


@app.route('/faculty/edit/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
def edit_faculty(faculty_id):
    """Edit an existing faculty member."""
    try:
        faculty_member = db.query_one("SELECT * FROM faculty WHERE faculty_id = %s", (faculty_id,))
        departments = db.query_all("SELECT dept_id, dept_name, dept_code FROM departments ORDER BY dept_name ASC")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return redirect(url_for('faculty'))

    if not faculty_member:
        flash("Faculty member not found.", "danger")
        return redirect(url_for('faculty'))

    if request.method == 'POST':
        faculty_name = request.form.get('faculty_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip() or None
        dept_id = request.form.get('dept_id', '').strip()

        try:
            sql = "UPDATE faculty SET faculty_name = %s, email = %s, phone = %s, dept_id = %s WHERE faculty_id = %s"
            db.execute_query(sql, (faculty_name, email, phone, dept_id, faculty_id))
            flash(f"Faculty member '{faculty_name}' updated successfully!", "success")
            return redirect(url_for('faculty'))
        except mysql.connector.IntegrityError:
            flash(f"Error: Email '{email}' is already in use by another faculty member.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('faculty_form.html', active_page='faculty', action='Edit', departments=departments, faculty_member=faculty_member)


@app.route('/faculty/delete/<int:faculty_id>', methods=['POST'])
@login_required
def delete_faculty(faculty_id):
    """Delete a faculty member safely, preventing orphaned course assignments."""
    try:
        db.execute_query("DELETE FROM faculty WHERE faculty_id = %s", (faculty_id,))
        flash("Faculty member deleted successfully.", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete faculty member: They are currently assigned as instructor to active courses. Reassign those courses first.", "danger")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
    return redirect(url_for('faculty'))


# ====================================================================
# MODULE 5: DEPARTMENT MANAGEMENT (Add, View, Edit, Delete)
# ====================================================================

@app.route('/departments')
@login_required
def departments():
    """List departments with associated student and faculty counts."""
    try:
        sql = """SELECT d.dept_id, d.dept_name, d.dept_code,
                        COUNT(DISTINCT s.student_id) AS student_count,
                        COUNT(DISTINCT f.faculty_id) AS faculty_count
                 FROM departments d
                 LEFT JOIN students s ON d.dept_id = s.dept_id
                 LEFT JOIN faculty f ON d.dept_id = f.dept_id
                 GROUP BY d.dept_id, d.dept_name, d.dept_code
                 ORDER BY d.dept_name ASC"""
        dept_list = db.query_all(sql)
        return render_template('departments.html', active_page='departments', departments=dept_list)
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return render_template('departments.html', active_page='departments', departments=[])


@app.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    """Create a new academic department."""
    if request.method == 'POST':
        dept_name = request.form.get('dept_name', '').strip()
        dept_code = request.form.get('dept_code', '').strip().upper()

        if not (dept_name and dept_code):
            flash("Department Name and Code are required.", "danger")
            return render_template('department_form.html', active_page='departments', action='Add', department=None)

        try:
            sql = "INSERT INTO departments (dept_name, dept_code) VALUES (%s, %s)"
            db.execute_query(sql, (dept_name, dept_code))
            flash(f"Department '{dept_name}' ({dept_code}) created successfully!", "success")
            return redirect(url_for('departments'))
        except mysql.connector.IntegrityError as err:
            flash("Error: Department Name or Department Code already exists.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('department_form.html', active_page='departments', action='Add', department=None)


@app.route('/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    """Edit an existing department."""
    try:
        dept = db.query_one("SELECT * FROM departments WHERE dept_id = %s", (dept_id,))
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return redirect(url_for('departments'))

    if not dept:
        flash("Department not found.", "danger")
        return redirect(url_for('departments'))

    if request.method == 'POST':
        dept_name = request.form.get('dept_name', '').strip()
        dept_code = request.form.get('dept_code', '').strip().upper()

        try:
            sql = "UPDATE departments SET dept_name = %s, dept_code = %s WHERE dept_id = %s"
            db.execute_query(sql, (dept_name, dept_code, dept_id))
            flash(f"Department updated to '{dept_name}' ({dept_code})!", "success")
            return redirect(url_for('departments'))
        except mysql.connector.IntegrityError:
            flash("Error: Department Name or Department Code already in use.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('department_form.html', active_page='departments', action='Edit', department=dept)


@app.route('/departments/delete/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    """Prevent unsafe deletion of departments referenced by students or faculty."""
    try:
        db.execute_query("DELETE FROM departments WHERE dept_id = %s", (dept_id,))
        flash("Department deleted successfully.", "success")
    except mysql.connector.IntegrityError:
        flash("Cannot delete department: It has enrolled students, assigned faculty, or active courses. Foreign Key RESTRICT constraint prevented unsafe deletion.", "danger")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
    return redirect(url_for('departments'))


# ====================================================================
# MODULE 6: COURSE MANAGEMENT (Add, View, Edit, Delete)
# ====================================================================

@app.route('/courses')
@login_required
def courses():
    """List all courses with department, faculty instructor, and semester info."""
    try:
        sql = """SELECT c.*, d.dept_name, d.dept_code, f.faculty_name, sem.semester_name, sem.academic_year
                 FROM courses c
                 INNER JOIN departments d ON c.dept_id = d.dept_id
                 INNER JOIN faculty f ON c.faculty_id = f.faculty_id
                 INNER JOIN semesters sem ON c.semester_id = sem.semester_id
                 ORDER BY c.course_id DESC"""
        courses_list = db.query_all(sql)
        return render_template('courses.html', active_page='courses', courses=courses_list)
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return render_template('courses.html', active_page='courses', courses=[])


@app.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    """Add a new course with dropdown selections from MySQL."""
    try:
        departments = db.query_all("SELECT dept_id, dept_name, dept_code FROM departments ORDER BY dept_name ASC")
        faculty_list = db.query_all("""SELECT f.faculty_id, f.faculty_name, d.dept_code 
                                       FROM faculty f 
                                       JOIN departments d ON f.dept_id = d.dept_id 
                                       ORDER BY f.faculty_name ASC""")
        semesters = db.query_all("SELECT semester_id, semester_name, academic_year FROM semesters ORDER BY semester_id ASC")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        departments, faculty_list, semesters = [], [], []

    if request.method == 'POST':
        course_code = request.form.get('course_code', '').strip().upper()
        course_name = request.form.get('course_name', '').strip()
        credits_val = request.form.get('credits', '').strip()
        dept_id = request.form.get('dept_id', '').strip()
        faculty_id = request.form.get('faculty_id', '').strip()
        semester_id = request.form.get('semester_id', '').strip()

        if not (course_code and course_name and credits_val and dept_id and faculty_id and semester_id):
            flash("All course fields are required.", "danger")
            return render_template('course_form.html', active_page='courses', action='Add',
                                   departments=departments, faculty_list=faculty_list, semesters=semesters, course=None)

        try:
            sql = """INSERT INTO courses (course_code, course_name, credits, dept_id, faculty_id, semester_id)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            db.execute_query(sql, (course_code, course_name, int(credits_val), dept_id, faculty_id, semester_id))
            flash(f"Course '{course_name}' ({course_code}) added successfully!", "success")
            return redirect(url_for('courses'))
        except mysql.connector.IntegrityError:
            flash(f"Error: Course Code '{course_code}' is already assigned to an existing course.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('course_form.html', active_page='courses', action='Add',
                           departments=departments, faculty_list=faculty_list, semesters=semesters, course=None)


@app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Edit course details."""
    try:
        course = db.query_one("SELECT * FROM courses WHERE course_id = %s", (course_id,))
        departments = db.query_all("SELECT dept_id, dept_name, dept_code FROM departments ORDER BY dept_name ASC")
        faculty_list = db.query_all("""SELECT f.faculty_id, f.faculty_name, d.dept_code 
                                       FROM faculty f 
                                       JOIN departments d ON f.dept_id = d.dept_id 
                                       ORDER BY f.faculty_name ASC""")
        semesters = db.query_all("SELECT semester_id, semester_name, academic_year FROM semesters ORDER BY semester_id ASC")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return redirect(url_for('courses'))

    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for('courses'))

    if request.method == 'POST':
        course_code = request.form.get('course_code', '').strip().upper()
        course_name = request.form.get('course_name', '').strip()
        credits_val = request.form.get('credits', '').strip()
        dept_id = request.form.get('dept_id', '').strip()
        faculty_id = request.form.get('faculty_id', '').strip()
        semester_id = request.form.get('semester_id', '').strip()

        try:
            sql = """UPDATE courses 
                     SET course_code = %s, course_name = %s, credits = %s, dept_id = %s, faculty_id = %s, semester_id = %s
                     WHERE course_id = %s"""
            db.execute_query(sql, (course_code, course_name, int(credits_val), dept_id, faculty_id, semester_id, course_id))
            flash(f"Course '{course_name}' updated successfully!", "success")
            return redirect(url_for('courses'))
        except mysql.connector.IntegrityError:
            flash(f"Error: Course Code '{course_code}' is already used by another subject.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('course_form.html', active_page='courses', action='Edit',
                           departments=departments, faculty_list=faculty_list, semesters=semesters, course=course)


@app.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    """Delete a course safely."""
    try:
        db.execute_query("DELETE FROM courses WHERE course_id = %s", (course_id,))
        flash("Course deleted successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
    return redirect(url_for('courses'))


# ====================================================================
# MODULE 7: STUDENT ENROLLMENTS
# ====================================================================

@app.route('/enrollments', methods=['GET', 'POST'])
@login_required
def enrollments():
    """Manage course enrollments and register students."""
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        course_id = request.form.get('course_id', '').strip()

        if not (student_id and course_id):
            flash("Please choose both a student and a course to register.", "danger")
        else:
            try:
                insert_sql = "INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (%s, %s, %s)"
                db.execute_query(insert_sql, (student_id, course_id, date.today()))
                flash("Student enrolled into course successfully!", "success")
                return redirect(url_for('enrollments'))
            except mysql.connector.IntegrityError:
                flash("Duplicate Registration Prevented: This student is already enrolled in the selected course.", "danger")
            except mysql.connector.Error as err:
                flash(f"Database Error: {err.msg}", "danger")

    try:
        # Fetch existing enrollments
        enrollments_sql = """SELECT e.enrollment_id, e.enrollment_date,
                                    s.roll_number, s.full_name AS student_name,
                                    c.course_code, c.course_name, c.credits,
                                    d.dept_name, f.faculty_name
                             FROM enrollments e
                             INNER JOIN students s ON e.student_id = s.student_id
                             INNER JOIN courses c ON e.course_id = c.course_id
                             INNER JOIN departments d ON c.dept_id = d.dept_id
                             INNER JOIN faculty f ON c.faculty_id = f.faculty_id
                             ORDER BY e.enrollment_id DESC"""
        enrollments_list = db.query_all(enrollments_sql)

        # Options for dropdowns
        students_options = db.query_all("""SELECT s.student_id, s.roll_number, s.full_name, d.dept_code 
                                           FROM students s 
                                           JOIN departments d ON s.dept_id = d.dept_id 
                                           ORDER BY s.roll_number ASC""")
        courses_options = db.query_all("SELECT course_id, course_code, course_name, credits FROM courses ORDER BY course_code ASC")

        return render_template(
            'enrollments.html',
            active_page='enrollments',
            enrollments=enrollments_list,
            students=students_options,
            courses=courses_options
        )
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return render_template('enrollments.html', active_page='enrollments', enrollments=[], students=[], courses=[])


@app.route('/enrollments/delete/<int:enrollment_id>', methods=['POST'])
@login_required
def delete_enrollment(enrollment_id):
    """Remove a course enrollment (cascades to related attendance and exam records)."""
    try:
        db.execute_query("DELETE FROM enrollments WHERE enrollment_id = %s", (enrollment_id,))
        flash("Student course enrollment removed successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
    return redirect(url_for('enrollments'))


# ====================================================================
# MODULE 8: ATTENDANCE MANAGEMENT
# ====================================================================

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    """Record attendance, prevent duplicate entries, and calculate attendance percentages."""
    if request.method == 'POST':
        enrollment_id = request.form.get('enrollment_id', '').strip()
        attendance_date = request.form.get('attendance_date', '').strip()
        status_val = request.form.get('status', '').strip()
        remarks = request.form.get('remarks', '').strip() or None

        if not (enrollment_id and attendance_date and status_val):
            flash("Enrollment, Date, and Attendance Status are required.", "danger")
        else:
            try:
                insert_sql = """INSERT INTO attendance (enrollment_id, attendance_date, status, remarks)
                                VALUES (%s, %s, %s, %s)"""
                db.execute_query(insert_sql, (enrollment_id, attendance_date, status_val, remarks))
                flash("Attendance recorded successfully in MySQL!", "success")
                return redirect(url_for('attendance'))
            except mysql.connector.IntegrityError:
                flash(f"Duplicate Attendance Prevented: An entry for this student and course already exists on {attendance_date}. You can use the 'Toggle' button in the log below to correct it.", "danger")
            except mysql.connector.Error as err:
                flash(f"Database Error: {err.msg}", "danger")

    try:
        # 1. Enrollment options for dropdown
        enrollment_options = db.query_all(
            """SELECT e.enrollment_id, s.roll_number, s.full_name AS student_name, c.course_code, c.course_name
               FROM enrollments e
               INNER JOIN students s ON e.student_id = s.student_id
               INNER JOIN courses c ON e.course_id = c.course_id
               ORDER BY s.roll_number, c.course_code"""
        )

        # 2. Student-wise Attendance Percentage: (Present Sessions / Total Sessions) * 100
        summary_sql = """SELECT s.roll_number, s.full_name AS student_name,
                                c.course_code, c.course_name,
                                COUNT(a.attendance_id) AS total_sessions,
                                SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_sessions,
                                ROUND(
                                    (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) * 100, 
                                    2
                                ) AS attendance_percentage
                         FROM enrollments e
                         INNER JOIN students s ON e.student_id = s.student_id
                         INNER JOIN courses c ON e.course_id = c.course_id
                         INNER JOIN attendance a ON e.enrollment_id = a.enrollment_id
                         GROUP BY e.enrollment_id, s.roll_number, s.full_name, c.course_code, c.course_name
                         ORDER BY attendance_percentage DESC"""
        attendance_summary = db.query_all(summary_sql)

        # 3. Full Attendance Records Log
        logs_sql = """SELECT a.attendance_id, a.attendance_date, a.status, a.remarks,
                             s.roll_number, s.full_name AS student_name,
                             c.course_code, c.course_name
                      FROM attendance a
                      INNER JOIN enrollments e ON a.enrollment_id = e.enrollment_id
                      INNER JOIN students s ON e.student_id = s.student_id
                      INNER JOIN courses c ON e.course_id = c.course_id
                      ORDER BY a.attendance_date DESC, a.attendance_id DESC
                      LIMIT 100"""
        attendance_logs = db.query_all(logs_sql)

        return render_template(
            'attendance.html',
            active_page='attendance',
            enrollment_options=enrollment_options,
            attendance_summary=attendance_summary,
            attendance_logs=attendance_logs,
            today_date=date.today().isoformat()
        )
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return render_template('attendance.html', active_page='attendance', enrollment_options=[], attendance_summary=[], attendance_logs=[], today_date=date.today().isoformat())


@app.route('/attendance/toggle/<int:attendance_id>', methods=['POST'])
@login_required
def toggle_attendance(attendance_id):
    """Quickly correct attendance entry between Present and Absent."""
    try:
        record = db.query_one("SELECT status FROM attendance WHERE attendance_id = %s", (attendance_id,))
        if record:
            new_status = 'Absent' if record['status'] == 'Present' else 'Present'
            db.execute_query("UPDATE attendance SET status = %s WHERE attendance_id = %s", (new_status, attendance_id))
            flash(f"Attendance record #{attendance_id} status changed to {new_status}.", "success")
        else:
            flash("Attendance record not found.", "danger")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
    return redirect(url_for('attendance'))


@app.route('/attendance/delete/<int:attendance_id>', methods=['POST'])
@login_required
def delete_attendance(attendance_id):
    """Delete an individual attendance log entry."""
    try:
        db.execute_query("DELETE FROM attendance WHERE attendance_id = %s", (attendance_id,))
        flash("Attendance record removed.", "success")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
    return redirect(url_for('attendance'))


# ====================================================================
# MODULE 9: EXAMINATION RESULTS
# ====================================================================

def calculate_grade(percentage):
    """Assign letter grade based on standardized institutional grading scale."""
    if percentage >= 90.0:
        return 'A+'
    elif percentage >= 80.0:
        return 'A'
    elif percentage >= 70.0:
        return 'B'
    elif percentage >= 60.0:
        return 'C'
    elif percentage >= 50.0:
        return 'D'
    else:
        return 'F'


@app.route('/exam_results', methods=['GET', 'POST'])
@login_required
def exam_results():
    """Add and view examination marks with percentage and letter grade calculation."""
    if request.method == 'POST':
        enrollment_id = request.form.get('enrollment_id', '').strip()
        exam_type = request.form.get('exam_type', '').strip()
        marks_obtained_str = request.form.get('marks_obtained', '').strip()
        max_marks_str = request.form.get('max_marks', '').strip()
        exam_date_str = request.form.get('exam_date', '').strip() or None

        try:
            marks_obtained = float(marks_obtained_str)
            max_marks = float(max_marks_str)

            # Validation: marks must be between 0 and maximum marks
            if marks_obtained < 0 or max_marks <= 0 or marks_obtained > max_marks:
                flash(f"Invalid Marks: Marks obtained ({marks_obtained}) must be between 0 and maximum marks ({max_marks}).", "danger")
                return redirect(url_for('exam_results'))

            percentage = round((marks_obtained / max_marks) * 100, 2)
            grade = calculate_grade(percentage)

            insert_sql = """INSERT INTO exam_results 
                            (enrollment_id, exam_type, marks_obtained, max_marks, percentage, grade, exam_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            db.execute_query(insert_sql, (enrollment_id, exam_type, marks_obtained, max_marks, percentage, grade, exam_date_str))
            flash(f"Examination result saved: Score {marks_obtained}/{max_marks} ({percentage}%), Grade: {grade}!", "success")
            return redirect(url_for('exam_results'))
        except ValueError:
            flash("Invalid input: Please enter numerical values for marks.", "danger")
        except mysql.connector.IntegrityError:
            flash(f"Duplicate Result: A result for exam '{exam_type}' has already been published for this enrollment. Edit or delete the existing record.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    try:
        # Enrollment options
        enrollment_options = db.query_all(
            """SELECT e.enrollment_id, s.roll_number, s.full_name AS student_name, c.course_code, c.course_name
               FROM enrollments e
               INNER JOIN students s ON e.student_id = s.student_id
               INNER JOIN courses c ON e.course_id = c.course_id
               ORDER BY s.roll_number, c.course_code"""
        )

        # Published examination results
        results_sql = """SELECT r.*, s.roll_number, s.full_name AS student_name, c.course_code, c.course_name
                         FROM exam_results r
                         INNER JOIN enrollments e ON r.enrollment_id = e.enrollment_id
                         INNER JOIN students s ON e.student_id = s.student_id
                         INNER JOIN courses c ON e.course_id = c.course_id
                         ORDER BY r.result_id DESC"""
        results_list = db.query_all(results_sql)

        return render_template(
            'exam_results.html',
            active_page='exam_results',
            enrollment_options=enrollment_options,
            results=results_list,
            today_date=date.today().isoformat()
        )
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return render_template('exam_results.html', active_page='exam_results', enrollment_options=[], results=[], today_date=date.today().isoformat())


@app.route('/exam_results/edit/<int:result_id>', methods=['GET', 'POST'])
@login_required
def edit_exam_result(result_id):
    """Edit an examination result record and recalculate percentage and grade."""
    try:
        result_sql = """SELECT r.*, s.roll_number, s.full_name AS student_name, c.course_code, c.course_name
                        FROM exam_results r
                        INNER JOIN enrollments e ON r.enrollment_id = e.enrollment_id
                        INNER JOIN students s ON e.student_id = s.student_id
                        INNER JOIN courses c ON e.course_id = c.course_id
                        WHERE r.result_id = %s"""
        result_item = db.query_one(result_sql, (result_id,))
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
        return redirect(url_for('exam_results'))

    if not result_item:
        flash("Examination result not found.", "danger")
        return redirect(url_for('exam_results'))

    if request.method == 'POST':
        exam_type = request.form.get('exam_type', '').strip()
        marks_obtained_str = request.form.get('marks_obtained', '').strip()
        max_marks_str = request.form.get('max_marks', '').strip()
        exam_date_str = request.form.get('exam_date', '').strip() or None

        try:
            marks_obtained = float(marks_obtained_str)
            max_marks = float(max_marks_str)

            if marks_obtained < 0 or max_marks <= 0 or marks_obtained > max_marks:
                flash(f"Invalid Marks: Marks obtained must be between 0 and {max_marks}.", "danger")
                return render_template('exam_result_form.html', active_page='exam_results', result=result_item)

            percentage = round((marks_obtained / max_marks) * 100, 2)
            grade = calculate_grade(percentage)

            update_sql = """UPDATE exam_results 
                            SET exam_type = %s, marks_obtained = %s, max_marks = %s, percentage = %s, grade = %s, exam_date = %s
                            WHERE result_id = %s"""
            db.execute_query(update_sql, (exam_type, marks_obtained, max_marks, percentage, grade, exam_date_str, result_id))
            flash(f"Result updated: Score {marks_obtained}/{max_marks} ({percentage}%), Grade: {grade}!", "success")
            return redirect(url_for('exam_results'))
        except ValueError:
            flash("Invalid input: Please enter numerical values for marks.", "danger")
        except mysql.connector.IntegrityError:
            flash("Error: An exam of that type already exists for this enrollment.", "danger")
        except mysql.connector.Error as err:
            flash(f"Database Error: {err.msg}", "danger")

    return render_template('exam_result_form.html', active_page='exam_results', result=result_item)


@app.route('/exam_results/delete/<int:result_id>', methods=['POST'])
@login_required
def delete_exam_result(result_id):
    """Delete an examination result entry."""
    try:
        db.execute_query("DELETE FROM exam_results WHERE result_id = %s", (result_id,))
        flash("Examination result record deleted.", "success")
    except mysql.connector.Error as err:
        flash(f"Database Error: {err.msg}", "danger")
    return redirect(url_for('exam_results'))


# ====================================================================
# ERROR HANDLING
# ====================================================================

@app.errorhandler(404)
def not_found(e):
    flash("The requested page was not found.", "warning")
    return redirect(url_for('dashboard'))


@app.errorhandler(500)
def server_error(e):
    flash("An unexpected server error occurred.", "danger")
    return redirect(url_for('dashboard'))


# ====================================================================
# APPLICATION ENTRYPOINT
# ====================================================================

if __name__ == '__main__':
    # Print status check to terminal on startup
    is_connected, error_msg = db.check_db_connection()
    print("=" * 65)
    print("  STUDENT AND COLLEGE MANAGEMENT SYSTEM (DBMS PBL)")
    if is_connected:
        print("  [SUCCESS] Connected to MySQL database successfully!")
    else:
        print(f"  [NOTICE] MySQL connection status: {error_msg}")
        print("  Please ensure your .env configuration has correct MySQL credentials.")
    print("  Server launching at: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host='127.0.0.1', port=5000, debug=Config.DEBUG)
