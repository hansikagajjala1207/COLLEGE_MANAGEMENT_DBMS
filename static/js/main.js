// ====================================================================
// College Management System - JavaScript Helpers
// ====================================================================

document.addEventListener('DOMContentLoaded', function () {
    // 1. Automatic Dismissal for Flash Messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // 2. Safe Delete Confirmation Handler
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const itemName = form.getAttribute('data-item-name') || 'this record';
            const confirmed = confirm(`Are you sure you want to permanently delete ${itemName}? This action cannot be undone.`);
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });

    // 3. Exam Results Form: Live Marks to Percentage & Grade Calculation
    const marksObtainedInput = document.getElementById('marks_obtained');
    const maxMarksInput = document.getElementById('max_marks');
    const percentagePreview = document.getElementById('percentage_preview');
    const gradePreview = document.getElementById('grade_preview');

    function calculateGrade() {
        if (!marksObtainedInput || !maxMarksInput) return;
        const marks = parseFloat(marksObtainedInput.value);
        const maxMarks = parseFloat(maxMarksInput.value);

        if (!isNaN(marks) && !isNaN(maxMarks) && maxMarks > 0) {
            const pct = ((marks / maxMarks) * 100).toFixed(2);
            let grade = 'F';
            if (pct >= 90) grade = 'A+';
            else if (pct >= 80) grade = 'A';
            else if (pct >= 70) grade = 'B';
            else if (pct >= 60) grade = 'C';
            else if (pct >= 50) grade = 'D';

            if (percentagePreview) percentagePreview.textContent = `${pct}%`;
            if (gradePreview) gradePreview.textContent = grade;
        } else {
            if (percentagePreview) percentagePreview.textContent = '--';
            if (gradePreview) gradePreview.textContent = '--';
        }
    }

    if (marksObtainedInput && maxMarksInput) {
        marksObtainedInput.addEventListener('input', calculateGrade);
        maxMarksInput.addEventListener('input', calculateGrade);
        calculateGrade();
    }
});
