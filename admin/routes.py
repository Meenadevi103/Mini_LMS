from flask import render_template, flash, redirect, url_for
from app import db
from app.admin import bp
from app.decorators import admin_required
from app.models import User, Course, Enrollment 
from flask_login import login_required

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users_count = User.query.count()
    courses_count = Course.query.count()
    enrollment_count = Enrollment.query.count()
    users = User.query.all()
    courses = Course.query.all()
    return render_template('admin/dashboard.html', users=users, courses=courses, 
                           users_count=users_count, courses_count=courses_count, enrollment_count=enrollment_count)

@bp.route('/activate_user/<int:user_id>')
@login_required
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_user = True
    db.session.commit()
    flash('User has been activated.')
    return redirect(url_for('admin.dashboard'))

@bp.route('/deactivate_user/<int:user_id>')
@login_required
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_user = False
    db.session.commit()
    flash('User has been deactivated.')
    return redirect(url_for('admin.dashboard'))

@bp.route('/delete_course/<int:course_id>')
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.')
    return redirect(url_for('admin.dashboard'))
