from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import (MembershipApplication, Resource, SavedResource,
                        EventRegistration, Notification, Event)
from app.extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


def require_user(f):
    """Decorator: redirect admins to admin dashboard."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return login_required(decorated)


@dashboard_bp.route('/')
@require_user
def index():
    membership = MembershipApplication.query.filter_by(user_id=current_user.id).first()
    saved      = SavedResource.query.filter_by(user_id=current_user.id).count()
    events_reg = EventRegistration.query.filter_by(user_id=current_user.id).count()
    notifs     = Notification.query.filter_by(user_id=current_user.id)\
                    .order_by(Notification.created_at.desc()).limit(10).all()
    unread     = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    upcoming   = (EventRegistration.query
                  .filter_by(user_id=current_user.id)
                  .join(Event)
                  .filter(Event.event_date >= __import__('datetime').datetime.utcnow())
                  .order_by(Event.event_date)
                  .limit(3).all())

    return render_template('dashboard/index.html',
        membership=membership,
        saved_count=saved,
        events_count=events_reg,
        notifications=notifs,
        unread_count=unread,
        upcoming_events=upcoming,
    )


@dashboard_bp.route('/profile')
@require_user
def profile():
    return render_template('dashboard/profile.html')


@dashboard_bp.route('/resources')
@require_user
def saved_resources():
    saved = (SavedResource.query
             .filter_by(user_id=current_user.id)
             .join(Resource)
             .all())
    return render_template('dashboard/resources.html', saved=saved)


@dashboard_bp.route('/resources/save/<int:resource_id>', methods=['POST'])
@login_required
def save_resource(resource_id):
    existing = SavedResource.query.filter_by(
        user_id=current_user.id, resource_id=resource_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed'})
    sr = SavedResource(user_id=current_user.id, resource_id=resource_id)
    db.session.add(sr)
    db.session.commit()
    return jsonify({'status': 'saved'})


@dashboard_bp.route('/events')
@require_user
def events():
    regs = (EventRegistration.query
            .filter_by(user_id=current_user.id)
            .join(Event)
            .order_by(Event.event_date.desc())
            .all())
    from datetime import datetime
    return render_template('dashboard/events.html', registrations=regs, now=datetime.utcnow())


@dashboard_bp.route('/events/register/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    existing = EventRegistration.query.filter_by(
        user_id=current_user.id, event_id=event_id).first()
    if existing:
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('public.news'))

    reg = EventRegistration(user_id=current_user.id, event_id=event_id)
    db.session.add(reg)

    notif = Notification(
        user_id=current_user.id,
        message=f'Successfully registered for: {event.title}',
        link=url_for('dashboard.events'),
    )
    db.session.add(notif)
    db.session.commit()
    flash(f'Registered for "{event.title}"!', 'success')
    return redirect(url_for('public.news'))


@dashboard_bp.route('/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    return jsonify({'status': 'ok'})
