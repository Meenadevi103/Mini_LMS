from flask import render_template, flash, redirect, url_for, request
from app import db
from app.teacher import bp
from app.decorators import teacher_required
from app.models import Course, Material, Assignment, Submission
from app.forms import CourseForm, MaterialForm, AssignmentForm
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from flask import current_app

@bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    courses = current_user.courses_taught.all()
    return render_template('teacher/dashboard.html', courses=courses)

@bp.route('/create_course', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(title=form.title.data, description=form.description.data, teacher_id=current_user.id)
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!')
        return redirect(url_for('teacher.dashboard'))
    return render_template('teacher/create_course.html', form=form, title='Create Course')

@bp.route('/course/<int:course_id>')
@login_required
@teacher_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('You are not authorized to view this course.')
        return redirect(url_for('teacher.dashboard'))
    return render_template('teacher/course_details.html', course=course)

@bp.route('/course/<int:course_id>/add_material', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_material(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        return redirect(url_for('teacher.dashboard'))
        
    form = MaterialForm()
    if form.validate_on_submit():
        content = form.content.data
        if form.material_type.data == 'pdf' and form.file.data:
            f = form.file.data
            filename = secure_filename(f.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            f.save(os.path.join(upload_folder, filename))
            content = filename
            
        material = Material(title=form.title.data, material_type=form.material_type.data, content=content, course_id=course.id)
        db.session.add(material)
        db.session.commit()
        flash('Material added.')
        return redirect(url_for('teacher.course_details', course_id=course.id))
    return render_template('teacher/add_material.html', form=form, title='Add Material')

@bp.route('/course/<int:course_id>/add_assignment', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_assignment(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        return redirect(url_for('teacher.dashboard'))
    
    form = AssignmentForm()
    if form.validate_on_submit():
        try:
             from datetime import datetime
             due_date = datetime.strptime(form.due_date.data, '%Y-%m-%d %H:%M')
        except ValueError:
             flash('Invalid date format. Use YYYY-MM-DD HH:MM')
             return render_template('teacher/add_assignment.html', form=form, title='Add Assignment')

        assignment = Assignment(title=form.title.data, description=form.description.data, due_date=due_date, course_id=course.id)
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created.')
        return redirect(url_for('teacher.course_details', course_id=course.id))
    return render_template('teacher/add_assignment.html', form=form, title='Add Assignment')

@bp.route('/assignment/<int:assignment_id>/submissions')
@login_required
@teacher_required
def view_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.teacher_id != current_user.id:
        return redirect(url_for('teacher.dashboard'))
    
    submissions = assignment.submissions.all()
    return render_template('teacher/view_submissions.html', assignment=assignment, submissions=submissions)
