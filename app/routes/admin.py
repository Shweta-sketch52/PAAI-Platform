from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models import (User, MembershipApplication, ContactMessage,
                        NewsPost, Event, Resource, FAQ, Notification)
from app.forms import NewsForm, EventForm, ResourceForm, FAQForm
from app.extensions import db
from datetime import datetime
import os, uuid
from markupsafe import escape as _escape
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)



def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('public.home'))
        return f(*args, **kwargs)
    return decorated


def save_uploaded_file(file, folder='uploads'):
    if not file or file.filename == '':
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    from flask import current_app
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return filename


def make_slug(title):
    import re
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    # Ensure uniqueness
    base = slug
    counter = 1
    while NewsPost.query.filter_by(slug=slug).first():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


# ─── DASHBOARD ───────────────────────────────────────────────────────────────
@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'total_users'       : User.query.count(),
        'pending_memberships': MembershipApplication.query.filter_by(status='pending').count(),
        'new_messages'      : ContactMessage.query.filter_by(is_read=False).count(),
        'total_news'        : NewsPost.query.count(),
        'total_events'      : Event.query.count(),
        'total_resources'   : Resource.query.count(),
        'total_faqs'        : FAQ.query.filter_by(is_active=True).count(),
    }
    pending_apps = MembershipApplication.query.filter_by(status='pending')\
        .order_by(MembershipApplication.submitted_at.desc()).limit(10).all()
    new_messages = ContactMessage.query.filter_by(is_read=False)\
        .order_by(ContactMessage.created_at.desc()).limit(6).all()
    from datetime import datetime as _dt
    return render_template('admin/dashboard.html', now=_dt.utcnow(),
        stats=stats, pending_apps=pending_apps, messages=new_messages)


# ─── USERS ───────────────────────────────────────────────────────────────────
@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:uid>/toggle', methods=['POST'])
@admin_required
def toggle_user(uid):
    user = User.query.get_or_404(uid)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot deactivate yourself'}), 400
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'is_active': user.is_active})


# ─── MEMBERSHIPS ─────────────────────────────────────────────────────────────
@admin_bp.route('/memberships')
@admin_required
def memberships():
    status = request.args.get('status', 'pending')
    apps = MembershipApplication.query.filter_by(status=status)\
        .order_by(MembershipApplication.submitted_at.desc()).all()
    return render_template('admin/memberships.html', applications=apps, active_status=status)


@admin_bp.route('/memberships/<int:app_id>/review', methods=['POST'])
@admin_required
def review_membership(app_id):
    application = MembershipApplication.query.get_or_404(app_id)
    action      = request.form.get('action')  # approve | reject
    notes       = request.form.get('notes', '')

    if action not in ('approve', 'reject'):
        flash('Invalid action.', 'danger')
        return redirect(url_for('admin.memberships'))

    application.status      = 'approved' if action == 'approve' else 'rejected'
    application.admin_notes = notes
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.utcnow()

    if application.user_id:
        notif = Notification(
            user_id = application.user_id,
            message = f'Your membership application has been {application.status}.',
            link    = url_for('dashboard.index'),
        )
        db.session.add(notif)

    db.session.commit()
    flash(f'Application {application.status}.', 'success')
    return redirect(url_for('admin.memberships'))


# ─── MESSAGES ────────────────────────────────────────────────────────────────
@admin_bp.route('/messages')
@admin_required
def messages():
    msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=msgs)


@admin_bp.route('/messages/<int:msg_id>/read', methods=['POST'])
@admin_required
def mark_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return jsonify({'status': 'ok'})


# ─── NEWS CMS ────────────────────────────────────────────────────────────────
@admin_bp.route('/news')
@admin_required
def news_list():
    posts = NewsPost.query.order_by(NewsPost.created_at.desc()).all()
    return render_template('admin/news_list.html', posts=posts)


@admin_bp.route('/news/new', methods=['GET', 'POST'])
@admin_required
def news_create():
    form = NewsForm()
    if form.validate_on_submit():
        image_file = save_uploaded_file(form.cover_image.data)
        post = NewsPost(
            title        = form.title.data,
            slug         = make_slug(form.title.data),
            category     = form.category.data,
            excerpt      = form.excerpt.data,
            content      = str(_escape(form.content.data)),
            cover_image  = image_file,
            author_id    = current_user.id,
            is_published = form.is_published.data,
            published_at = datetime.utcnow() if form.is_published.data else None,
        )
        db.session.add(post)
        db.session.commit()
        flash('News post created.', 'success')
        return redirect(url_for('admin.news_list'))
    return render_template('admin/news_form.html', form=form, title='Create Post')


@admin_bp.route('/news/<int:post_id>/edit', methods=['GET', 'POST'])
@admin_required
def news_edit(post_id):
    post = NewsPost.query.get_or_404(post_id)
    form = NewsForm(obj=post)
    if form.validate_on_submit():
        post.title    = form.title.data
        post.category = form.category.data
        post.excerpt  = form.excerpt.data
        post.content  = str(_escape(form.content.data))
        if form.cover_image.data:
            post.cover_image = save_uploaded_file(form.cover_image.data)
        if form.is_published.data and not post.is_published:
            post.published_at = datetime.utcnow()
        post.is_published = form.is_published.data
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('admin.news_list'))
    return render_template('admin/news_form.html', form=form, title='Edit Post', post=post)


@admin_bp.route('/news/<int:post_id>/delete', methods=['POST'])
@admin_required
def news_delete(post_id):
    post = NewsPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('admin.news_list'))


# ─── EVENTS CMS ──────────────────────────────────────────────────────────────
@admin_bp.route('/events')
@admin_required
def events_list():
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin/events_list.html', events=events)


@admin_bp.route('/events/new', methods=['GET', 'POST'])
@admin_required
def event_create():
    form = EventForm()
    if form.validate_on_submit():
        image_file = save_uploaded_file(form.cover_image.data)
        ev = Event(
            title             = form.title.data,
            event_type        = form.event_type.data,
            description       = form.description.data,
            location          = form.location.data,
            event_date        = form.event_date.data,
            capacity          = int(form.capacity.data) if form.capacity.data else None,
            is_free           = form.is_free.data,
            registration_link = form.registration_link.data,
            cover_image       = image_file,
            is_published      = form.is_published.data,
        )
        db.session.add(ev)
        db.session.commit()
        flash('Event created.', 'success')
        return redirect(url_for('admin.events_list'))
    return render_template('admin/event_form.html', form=form, title='Create Event')


@admin_bp.route('/events/<int:ev_id>/delete', methods=['POST'])
@admin_required
def event_delete(ev_id):
    ev = Event.query.get_or_404(ev_id)
    db.session.delete(ev)
    db.session.commit()
    flash('Event deleted.', 'success')
    return redirect(url_for('admin.events_list'))


# ─── RESOURCES CMS ───────────────────────────────────────────────────────────
@admin_bp.route('/resources')
@admin_required
def resources_list():
    resources = Resource.query.order_by(Resource.created_at.desc()).all()
    return render_template('admin/resources_list.html', resources=resources)


@admin_bp.route('/resources/new', methods=['GET', 'POST'])
@admin_required
def resource_create():
    form = ResourceForm()
    if form.validate_on_submit():
        file_path = save_uploaded_file(form.file_upload.data)
        res = Resource(
            title         = form.title.data,
            category      = form.category.data,
            resource_type = form.resource_type.data,
            description   = form.description.data,
            file_path     = file_path,
            external_url  = form.external_url.data,
            language      = form.language.data,
            is_published  = form.is_published.data,
        )
        db.session.add(res)
        db.session.commit()
        flash('Resource added.', 'success')
        return redirect(url_for('admin.resources_list'))
    return render_template('admin/resource_form.html', form=form, title='Add Resource')


@admin_bp.route('/resources/<int:res_id>/delete', methods=['POST'])
@admin_required
def resource_delete(res_id):
    res = Resource.query.get_or_404(res_id)
    db.session.delete(res)
    db.session.commit()
    flash('Resource deleted.', 'success')
    return redirect(url_for('admin.resources_list'))


# ─── FAQ CMS ─────────────────────────────────────────────────────────────────
@admin_bp.route('/faqs')
@admin_required
def faqs_list():
    faqs = FAQ.query.order_by(FAQ.order, FAQ.category).all()
    return render_template('admin/faqs_list.html', faqs=faqs)


@admin_bp.route('/faqs/new', methods=['GET', 'POST'])
@admin_required
def faq_create():
    form = FAQForm()
    if form.validate_on_submit():
        faq = FAQ(
            question  = form.question.data,
            answer    = form.answer.data,
            category  = form.category.data,
            keywords  = form.keywords.data,
            order     = int(form.order.data) if form.order.data else 0,
            is_active = form.is_active.data,
        )
        db.session.add(faq)
        db.session.commit()
        flash('FAQ added.', 'success')
        return redirect(url_for('admin.faqs_list'))
    return render_template('admin/faq_form.html', form=form, title='Add FAQ')


@admin_bp.route('/faqs/<int:faq_id>/delete', methods=['POST'])
@admin_required
def faq_delete(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ deleted.', 'success')
    return redirect(url_for('admin.faqs_list'))
