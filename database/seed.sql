-- ====================================================================
-- SEED DATA FOR STUDENT AND COLLEGE MANAGEMENT SYSTEM
-- Realistic fictional sample data (at least 5 records per table)
-- ====================================================================

USE student_college_management;

-- Disable foreign key checks momentarily for clean reload
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE exam_results;
TRUNCATE TABLE attendance;
TRUNCATE TABLE enrollments;
TRUNCATE TABLE courses;
TRUNCATE TABLE students;
TRUNCATE TABLE faculty;
TRUNCATE TABLE semesters;
TRUNCATE TABLE departments;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. USERS (Admin user: username='admin', password='admin123')
INSERT INTO users (user_id, username, password_hash, full_name, role) VALUES
(1, 'admin', 'scrypt:32768:8:1$CZkZSTJBgS9d55fQ$93916ae95e835fe4c858ca266eea469f8c71be2bc63c77fc59a0fb11b22971495dc779ac8be8219ce0d0568bec7a9a94101a82eb73096a9b9b22aee0c0ed1db0', 'System Administrator', 'Admin'),
(2, 'dean_office', 'scrypt:32768:8:1$CZkZSTJBgS9d55fQ$93916ae95e835fe4c858ca266eea469f8c71be2bc63c77fc59a0fb11b22971495dc779ac8be8219ce0d0568bec7a9a94101a82eb73096a9b9b22aee0c0ed1db0', 'Dean of Academics', 'Admin');

-- 2. DEPARTMENTS (5 Departments)
INSERT INTO departments (dept_id, dept_name, dept_code) VALUES
(1, 'Computer Science & Engineering', 'CSE'),
(2, 'Information Technology', 'IT'),
(3, 'Electronics & Communication Engineering', 'ECE'),
(4, 'Mechanical Engineering', 'ME'),
(5, 'Civil Engineering', 'CE');

-- 3. SEMESTERS (6 Semesters)
INSERT INTO semesters (semester_id, semester_name, academic_year) VALUES
(1, 'Semester 1', '2024-2025'),
(2, 'Semester 2', '2024-2025'),
(3, 'Semester 3', '2024-2025'),
(4, 'Semester 4', '2024-2025'),
(5, 'Semester 5', '2024-2025'),
(6, 'Semester 6', '2024-2025');

-- 4. FACULTY (5 Faculty Members)
INSERT INTO faculty (faculty_id, faculty_name, email, phone, dept_id) VALUES
(1, 'Dr. Rajesh Sharma', 'rajesh.sharma@college.edu', '9876543210', 1),
(2, 'Prof. Sunita Nair', 'sunita.nair@college.edu', '9876543211', 1),
(3, 'Dr. Amit Verma', 'amit.verma@college.edu', '9876543212', 2),
(4, 'Prof. Priya Kulkarni', 'priya.kulkarni@college.edu', '9876543213', 3),
(5, 'Dr. Ramesh Choudhury', 'ramesh.choudhury@college.edu', '9876543214', 4);

-- 5. STUDENTS (6 Students)
INSERT INTO students (student_id, roll_number, full_name, email, phone, dob, gender, dept_id, admission_year) VALUES
(1, '23CSE001', 'Aarav Patel', 'aarav.patel@student.edu', '9123456780', '2004-05-14', 'Male', 1, 2023),
(2, '23CSE002', 'Diya Sen', 'diya.sen@student.edu', '9123456781', '2004-08-22', 'Female', 1, 2023),
(3, '23IT001', 'Rohan Mehta', 'rohan.mehta@student.edu', '9123456782', '2004-02-11', 'Male', 2, 2023),
(4, '23ECE001', 'Ananya Iyer', 'ananya.iyer@student.edu', '9123456783', '2004-11-30', 'Female', 3, 2023),
(5, '23ME001', 'Vikram Singh', 'vikram.singh@student.edu', '9123456784', '2003-09-18', 'Male', 4, 2023),
(6, '23CE001', 'Pooja Reddy', 'pooja.reddy@student.edu', '9123456785', '2004-07-05', 'Female', 5, 2023);

-- 6. COURSES (6 Courses)
INSERT INTO courses (course_id, course_code, course_name, credits, dept_id, faculty_id, semester_id) VALUES
(1, 'CS301', 'Database Management Systems', 4, 1, 1, 3),
(2, 'CS302', 'Data Structures & Algorithms', 4, 1, 2, 3),
(3, 'IT301', 'Web Technologies & Frameworks', 3, 2, 3, 3),
(4, 'EC301', 'Digital Signal Processing', 4, 3, 4, 3),
(5, 'ME301', 'Thermodynamics & Heat Transfer', 4, 4, 5, 3),
(6, 'CS303', 'Operating Systems', 3, 1, 1, 3);

-- 7. ENROLLMENTS (8 Student-Course Registrations)
INSERT INTO enrollments (enrollment_id, student_id, course_id, enrollment_date) VALUES
(1, 1, 1, '2024-07-15'), -- Aarav -> DBMS
(2, 1, 2, '2024-07-15'), -- Aarav -> DSA
(3, 2, 1, '2024-07-15'), -- Diya -> DBMS
(4, 2, 2, '2024-07-15'), -- Diya -> DSA
(5, 3, 3, '2024-07-16'), -- Rohan -> Web Tech
(6, 4, 4, '2024-07-16'), -- Ananya -> DSP
(7, 5, 5, '2024-07-16'), -- Vikram -> Thermodynamics
(8, 1, 6, '2024-07-17'); -- Aarav -> OS

-- 8. ATTENDANCE (Sample records with Present / Absent)
INSERT INTO attendance (attendance_id, enrollment_id, attendance_date, status, remarks) VALUES
(1, 1, '2024-08-01', 'Present', 'Attended lecture & lab'),
(2, 1, '2024-08-02', 'Present', 'Regular'),
(3, 1, '2024-08-05', 'Absent', 'Medical leave'),
(4, 1, '2024-08-06', 'Present', 'Regular'),
(5, 3, '2024-08-01', 'Present', 'On time'),
(6, 3, '2024-08-02', 'Present', 'On time'),
(7, 3, '2024-08-05', 'Present', 'On time'),
(8, 5, '2024-08-01', 'Absent', 'Unexcused'),
(9, 5, '2024-08-02', 'Present', 'Present in lab'),
(10, 6, '2024-08-01', 'Present', 'Active participant');

-- 9. EXAM_RESULTS (Marks, percentages, letter grades)
INSERT INTO exam_results (result_id, enrollment_id, exam_type, marks_obtained, max_marks, percentage, grade, exam_date) VALUES
(1, 1, 'Mid-Term 1', 46.50, 50.00, 93.00, 'A+', '2024-09-10'),
(2, 1, 'Mid-Term 2', 43.00, 50.00, 86.00, 'A',  '2024-10-15'),
(3, 2, 'Mid-Term 1', 41.50, 50.00, 83.00, 'A',  '2024-09-11'),
(4, 3, 'Mid-Term 1', 48.00, 50.00, 96.00, 'A+', '2024-09-10'),
(5, 4, 'Mid-Term 1', 37.00, 50.00, 74.00, 'B',  '2024-09-11'),
(6, 5, 'Mid-Term 1', 32.50, 50.00, 65.00, 'C',  '2024-09-12'),
(7, 6, 'Mid-Term 1', 45.00, 50.00, 90.00, 'A+', '2024-09-12'),
(8, 7, 'Mid-Term 1', 28.00, 50.00, 56.00, 'D',  '2024-09-13');
