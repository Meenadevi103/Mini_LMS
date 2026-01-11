from flask import render_template, flash, redirect, url_for
from app import db
from app.student import bp
from app.decorators import student_required
from app.models import Course, Enrollment, Assignment, Submission
from app.forms import SubmissionForm
from flask_login import login_required, current_user

@bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    enrollments = current_user.enrollments.all()
    courses = [enrollment.course for enrollment in enrollments]
    return render_template('student/dashboard.html', courses=courses)

@bp.route('/available_courses')
@login_required
@student_required
def available_courses():
    all_courses = Course.query.all()
    enrolled_course_ids = [e.course_id for e in current_user.enrollments.all()]
    available = [c for c in all_courses if c.id not in enrolled_course_ids]
    return render_template('student/available_courses.html', courses=available)

@bp.route('/enroll/<int:course_id>')
@login_required
@student_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    if Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first():
        flash('Already enrolled in this course.')
        return redirect(url_for('student.dashboard'))
    
    enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()
    flash(f'You have enrolled in {course.title}.')
    return redirect(url_for('student.dashboard'))

@bp.route('/course/<int:course_id>')
@login_required
@student_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    if not Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first():
        flash('You are not enrolled in this course.')
        return redirect(url_for('student.available_courses'))
        
    return render_template('student/course_details.html', course=course)

@bp.route('/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
@student_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if not Enrollment.query.filter_by(student_id=current_user.id, course_id=assignment.course_id).first():
        flash('You are not enrolled in this course.')
        return redirect(url_for('student.dashboard'))

    form = SubmissionForm()
    if form.validate_on_submit():
        submission = Submission(assignment_id=assignment.id, student_id=current_user.id, content=form.content.data)
        db.session.add(submission)
        db.session.commit()
        flash('Assignment submitted.')
        return redirect(url_for('student.course_details', course_id=assignment.course_id))
    return render_template('student/submit_assignment.html', form=form, assignment=assignment)
