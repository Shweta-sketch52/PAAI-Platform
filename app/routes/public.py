from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import NewsPost, Event, Resource
from app.forms import ContactForm, MembershipForm
from app.extensions import db
from app.models import ContactMessage, MembershipApplication
from datetime import datetime

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def home():
    latest_news = NewsPost.query.filter_by(is_published=True)\
        .order_by(NewsPost.published_at.desc()).limit(3).all()
    upcoming_events = Event.query.filter(
        Event.is_published == True,
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date).limit(3).all()
    return render_template('public/home.html', news=latest_news, events=upcoming_events)


@public_bp.route('/about')
def about():
    return render_template('public/about.html')


@public_bp.route('/programs')
def programs():
    return render_template('public/programs.html')


@public_bp.route('/partners')
def partners():
    return render_template('public/about.html')


@public_bp.route('/resources')
def resources():
    category = request.args.get('category', '')
    query = Resource.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    all_resources = query.order_by(Resource.created_at.desc()).all()
    return render_template('public/resources.html', resources=all_resources, active_category=category)


@public_bp.route('/resources/download/<int:resource_id>')
def download_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    resource.download_count += 1
    db.session.commit()
    if resource.external_url:
        return redirect(resource.external_url)
    if resource.file_path:
        from flask import send_from_directory
        return send_from_directory('static/uploads', resource.file_path)
    flash('Resource file not available.', 'warning')
    return redirect(url_for('public.resources'))


@public_bp.route('/news')
def news():
    page = request.args.get('page', 1, type=int)
    news_posts = NewsPost.query.filter_by(is_published=True)\
        .order_by(NewsPost.published_at.desc())\
        .paginate(page=page, per_page=9, error_out=False)
    events = Event.query.filter(
        Event.is_published == True,
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date).limit(5).all()
    return render_template('public/news.html', news=news_posts, events=events)


@public_bp.route('/news/<slug>')
def news_detail(slug):
    post = NewsPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    related = NewsPost.query.filter(
        NewsPost.is_published == True,
        NewsPost.id != post.id
    ).limit(3).all()
    return render_template('public/news_detail.html', post=post, related=related)


@public_bp.route('/membership', methods=['GET', 'POST'])
def membership():
    form = MembershipForm()
    if form.validate_on_submit():
        application = MembershipApplication(
            full_name       = form.full_name.data,
            email           = form.email.data,
            phone           = form.phone.data,
            membership_type = form.membership_type.data,
            organization    = form.organization.data,
            city            = form.city.data,
            state           = form.state.data,
            message         = form.message.data,
        )
        db.session.add(application)
        db.session.commit()
        flash('Application submitted! We will review it within 5 business days.', 'success')
        return redirect(url_for('public.membership'))
    return render_template('public/membership.html', form=form)


@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name    = form.name.data,
            email   = form.email.data,
            subject = form.subject.data,
            message = form.message.data,
        )
        db.session.add(msg)
        db.session.commit()
        flash("Your message has been sent. We'll respond within 1-2 business days.", 'success')
        return redirect(url_for('public.contact'))
    return render_template('public/contact.html', form=form)
