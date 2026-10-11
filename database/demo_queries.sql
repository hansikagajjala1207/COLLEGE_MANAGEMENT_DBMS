-- ====================================================================
-- DEMONSTRATION SQL QUERIES FOR DBMS PRESENTATION / VIVA
-- Project: Student and College Management System
-- Database: student_college_management
-- ====================================================================

USE student_college_management;

-- --------------------------------------------------------------------
-- 1. SELECT all students with complete personal details
-- --------------------------------------------------------------------
SELECT 
    student_id,
    roll_number,
    full_name,
    email,
    phone,
    dob,
    gender,
    dept_id,
    admission_year
FROM students;

-- --------------------------------------------------------------------
-- 2. INSERT example: Adding a new test student record
-- --------------------------------------------------------------------
INSERT INTO students (roll_number, full_name, email, phone, dob, gender, dept_id, admission_year)
VALUES ('TEST999', 'Demo Test Student', 'demo.test@student.edu', '9999999999', '2004-01-01', 'Other', 1, 2024);

-- Verify insertion:
SELECT * FROM students WHERE roll_number = 'TEST999';

-- --------------------------------------------------------------------
-- 3. UPDATE example: Updating email and phone for the test student
-- --------------------------------------------------------------------
UPDATE students 
SET 
    email = 'updated.test@student.edu',
    phone = '9888888888'
WHERE roll_number = 'TEST999';

-- Verify update:
SELECT roll_number, full_name, email, phone FROM students WHERE roll_number = 'TEST999';

-- --------------------------------------------------------------------
-- 4. DELETE example: Safely deleting the dedicated test record
-- --------------------------------------------------------------------
DELETE FROM students 
WHERE roll_number = 'TEST999';

-- Verify deletion:
SELECT * FROM students WHERE roll_number = 'TEST999';

-- --------------------------------------------------------------------
-- 5. INNER JOIN: Retrieve students along with their department details
-- --------------------------------------------------------------------
SELECT 
    s.student_id,
    s.roll_number,
    s.full_name,
    s.email,
    d.dept_name,
    d.dept_code,
    s.admission_year
FROM students s
INNER JOIN departments d ON s.dept_id = d.dept_id
ORDER BY s.roll_number ASC;

-- --------------------------------------------------------------------
-- 6. MULTI-TABLE JOIN: Students with their enrolled courses & faculty
-- --------------------------------------------------------------------
SELECT 
    s.roll_number,
    s.full_name AS student_name,
    c.course_code,
    c.course_name,
    c.credits,
    f.faculty_name AS course_instructor,
    sem.semester_name
FROM enrollments e
INNER JOIN students s ON e.student_id = s.student_id
INNER JOIN courses c ON e.course_id = c.course_id
INNER JOIN faculty f ON c.faculty_id = f.faculty_id
INNER JOIN semesters sem ON c.semester_id = sem.semester_id
ORDER BY s.roll_number, c.course_code;

-- --------------------------------------------------------------------
-- 7. GROUP BY & COUNT: Department-wise total student strength
-- --------------------------------------------------------------------
SELECT 
    d.dept_code,
    d.dept_name,
    COUNT(s.student_id) AS total_enrolled_students
FROM departments d
LEFT JOIN students s ON d.dept_id = s.dept_id
GROUP BY d.dept_id, d.dept_code, d.dept_name
ORDER BY total_enrolled_students DESC;

-- --------------------------------------------------------------------
-- 8. GROUP BY & AVG: Average exam marks scored per course
-- --------------------------------------------------------------------
SELECT 
    c.course_code,
    c.course_name,
    COUNT(r.result_id) AS total_evaluations,
    ROUND(AVG(r.marks_obtained), 2) AS average_marks_obtained,
    ROUND(AVG(r.percentage), 2) AS average_percentage
FROM courses c
INNER JOIN enrollments e ON c.course_id = e.course_id
INNER JOIN exam_results r ON e.enrollment_id = r.enrollment_id
GROUP BY c.course_id, c.course_code, c.course_name
ORDER BY average_percentage DESC;

-- --------------------------------------------------------------------
-- 9. ATTENDANCE PERCENTAGE PER STUDENT:
-- Formula: (Present Sessions / Total Recorded Sessions) * 100
-- --------------------------------------------------------------------
SELECT 
    s.roll_number,
    s.full_name AS student_name,
    c.course_code,
    c.course_name,
    COUNT(a.attendance_id) AS total_sessions_conducted,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended_sessions,
    ROUND(
        (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) * 100, 
        2
    ) AS attendance_percentage
FROM enrollments e
INNER JOIN students s ON e.student_id = s.student_id
INNER JOIN courses c ON e.course_id = c.course_id
LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
GROUP BY e.enrollment_id, s.roll_number, s.full_name, c.course_code, c.course_name
HAVING total_sessions_conducted > 0
ORDER BY attendance_percentage DESC;

-- --------------------------------------------------------------------
-- 10. ORDER BY: Alphabetical student directory with contact info
-- --------------------------------------------------------------------
SELECT 
    full_name,
    roll_number,
    email,
    phone,
    gender
FROM students
ORDER BY full_name ASC;

-- --------------------------------------------------------------------
-- 11. WHERE filtering: Find all students belonging to CSE department
-- --------------------------------------------------------------------
SELECT 
    s.roll_number,
    s.full_name,
    s.email,
    d.dept_name
FROM students s
INNER JOIN departments d ON s.dept_id = d.dept_id
WHERE d.dept_code = 'CSE'
ORDER BY s.roll_number;

-- --------------------------------------------------------------------
-- 12. METADATA QUERY: Inspect Primary Keys, Foreign Keys, & Constraints
-- --------------------------------------------------------------------
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'student_college_management'
  AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, CONSTRAINT_NAME;
