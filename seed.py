"""
Run with: python seed.py
Seeds the database with sample data for development.
"""

from app.extensions import db
from app.models import (
    User,
    MembershipApplication,
    NewsPost,
    Event,
    Resource,
    FAQ,
    ContactMessage
)
from datetime import datetime, timedelta
import random


def seed():

    db.create_all()

    print("🌱 Seeding database...")

    # ── Admin user ──
    if not User.query.filter_by(email='admin@paai.org.in').first():
        admin = User(
            full_name='PAAI Admin',
            email='admin@paai.org.in',
            role='admin',
            is_active=True,
        )
        admin.set_password('Admin@PAAI2024!')
        db.session.add(admin)
        db.session.flush()
        print('  ✓ Admin user created')

    # ── Sample users ──
    sample_users = [
        ('Meera Sharma', 'meera@example.com', 'Delhi', 'Delhi'),
        ('Rajesh Kumar', 'rajesh@example.com', 'Mumbai', 'Maharashtra'),
        ('Dr. Anita Rao', 'anita@example.com', 'Bengaluru', 'Karnataka'),
    ]
    for name, email, city, state in sample_users:
        if not User.query.filter_by(email=email).first():
            u = User(full_name=name, email=email, city=city, state=state)
            u.set_password('User@1234!')
            db.session.add(u)
    db.session.flush()
    print('  ✓ Sample users created')

    # ── Membership applications ──
    apps_data = [
        ('Anjali Verma', 'anjali@example.com', 'Individual Advocate', None, 'Pune', 'Maharashtra', 'pending'),
        ('HealthBridge NGO', 'contact@healthbridge.org', 'NGO / Foundation', 'HealthBridge Foundation', 'Chennai', 'Tamil Nadu', 'pending'),
        ('Dr. Ramesh Gupta', 'ramesh@medcare.in', 'Healthcare Professional', 'MedCare Hospital', 'Jaipur', 'Rajasthan', 'pending'),
        ('Nirmala Devi', 'nirmala@gmail.com', 'Caregiver', None, 'Lucknow', 'Uttar Pradesh', 'approved'),
    ]
    for name, email, mtype, org, city, state, status in apps_data:
        if not MembershipApplication.query.filter_by(email=email).first():
            app_obj = MembershipApplication(
                full_name=name,
                email=email,
                membership_type=mtype,
                organization=org,
                city=city,
                state=state,
                status=status,
                message='I want to contribute to patient advocacy in India.',
            )
            db.session.add(app_obj)
    print('  ✓ Membership applications seeded')

    # ── News posts ──
    posts = [
        (
            'PAAI Advocacy Leads to Landmark Patient Rights Amendment',
            'policy-win-patient-rights-2024',
            'Policy Win',
            "After two years of sustained advocacy, the Ministry of Health accepted PAAI's recommendations.",
            "<p>In a landmark victory for patient advocacy, the Ministry of Health and Family Welfare has formally adopted PAAI's recommendations on informed consent and treatment transparency standards...</p>",
            True,
        ),
        (
            'Annual National Patient Advocacy Summit 2024 — Highlights',
            'advocacy-summit-2024',
            'Community',
            'Over 800 delegates from 28 states gathered in New Delhi.',
            '<p>The 12th Annual PAAI National Summit brought together an unprecedented 800+ delegates...</p>',
            True,
        ),
        (
            'PAAI Signs MoU with WHO India for Rare Disease Programme',
            'who-india-mou-2024',
            'Partnership',
            'A landmark collaboration to improve rare disease patient outcomes.',
            '<p>PAAI and WHO India have signed a Memorandum of Understanding to jointly develop a national rare disease support framework...</p>',
            True,
        ),
    ]
    for title, slug, cat, excerpt, content, published in posts:
        if not NewsPost.query.filter_by(slug=slug).first():
            post = NewsPost(
                title=title,
                slug=slug,
                category=cat,
                excerpt=excerpt,
                content=content,
                is_published=published,
                published_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                author_id=1,
            )
            db.session.add(post)
    print('  ✓ News posts seeded')

    # ── Events ──
    events_data = [
        (
            'Understanding Your Rights: PMJAY & Insurance Navigation',
            'Webinar',
            'Online (Zoom)',
            datetime.utcnow() + timedelta(days=20),
            True,
        ),
        (
            'Rare Disease Awareness Day — National Symposium 2025',
            'Conference',
            'AIIMS Auditorium, New Delhi',
            datetime.utcnow() + timedelta(days=38),
            True,
        ),
        (
            'Caregiver Wellbeing Workshop — Mumbai Chapter',
            'Workshop',
            'Kokilaben Hospital, Mumbai',
            datetime.utcnow() + timedelta(days=55),
            False,
        ),
    ]
    for title, etype, loc, edate, is_free in events_data:
        if not Event.query.filter_by(title=title).first():
            ev = Event(
                title=title,
                event_type=etype,
                location=loc,
                event_date=edate,
                is_free=is_free,
                is_published=True,
            )
            db.session.add(ev)
    print('  ✓ Events seeded')

    # ── Resources ──
    resources_data = [
        (
            'Know Your Healthcare Rights in India',
            'Patient Rights',
            'PDF',
            'Comprehensive guide to patient rights under Indian law.',
        ),
        (
            'Navigating Health Insurance Claims',
            'Insurance',
            'Toolkit',
            'Step-by-step toolkit for filing and appealing health insurance claims.',
        ),
        (
            'Mental Wellness for Patients & Caregivers',
            'Mental Health',
            'PDF',
            'Evidence-based strategies for managing chronic illness.',
        ),
        (
            'Rare Disease Advocacy Handbook',
            'Rare Disease',
            'PDF',
            'Practical guide for patients with rare diseases.',
        ),
        (
            'Caregiver Burnout Prevention Guide',
            'Caregiver',
            'PDF',
            'Self-assessment tools and coping strategies for caregivers.',
        ),
        (
            'Medical Negligence & Legal Recourse',
            'Legal',
            'PDF',
            'Understanding patient rights in cases of medical negligence.',
        ),
    ]
    for title, cat, rtype, desc in resources_data:
        if not Resource.query.filter_by(title=title).first():
            r = Resource(
                title=title,
                category=cat,
                resource_type=rtype,
                description=desc,
                is_published=True,
            )
            db.session.add(r)
    print('  ✓ Resources seeded')

    # ── FAQs ──
    faqs_data = [
        (
            'How do I join PAAI?',
            'To join PAAI, visit our Membership page and fill out the application form. We offer Individual Advocate, Organizational, and Corporate Partner tiers. Applications are reviewed within 5 business days.',
            'Membership',
            'join,member,apply,registration',
        ),
        (
            'What is the cost of membership?',
            'Individual Advocate membership is free for patients, caregivers, and patient community members. Organizational and Corporate memberships have nominal fees that support our programs. Contact info@paai.org.in for details.',
            'Membership',
            'cost,fee,price,paid,free',
        ),
        (
            'How can caregivers get support from PAAI?',
            'PAAI has dedicated caregiver support programs including peer support groups, skills training workshops, burnout prevention resources, and a helpline. Download our free Caregiver Wellness Guide from the Resources page.',
            'Programs',
            'caregiver,support,caring,family',
        ),
        (
            'Does PAAI help with insurance disputes?',
            'Yes! We offer a free Insurance Navigation Toolkit and can connect you with patient advocates who assist with PMJAY and private insurance disputes. Download the toolkit from our Resources page.',
            'Resources',
            'insurance,claim,dispute,PMJAY',
        ),
    ]
    for q, a, cat, kw in faqs_data:
        if not FAQ.query.filter_by(question=q).first():
            faq = FAQ(
                question=q,
                answer=a,
                category=cat,
                keywords=kw,
            )
            db.session.add(faq)
    print('  ✓ FAQs seeded')

    # ── Contact messages ──
    msgs_data = [
        (
            'Suresh Patel',
            'suresh@gmail.com',
            'Membership Query',
            'I would like to know more about joining PAAI as an individual advocate.',
        ),
        (
            'Nirmala Devi',
            'nirmala.d@yahoo.com',
            'Caregiver Support',
            "I am caring for my mother with Parkinson's and need guidance.",
        ),
    ]
    for name, email, subject, message in msgs_data:
        if not ContactMessage.query.filter_by(email=email).first():
            cm = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
            db.session.add(cm)
    print('  ✓ Contact messages seeded')

    db.session.commit()

    print('\n✅ Database seeded successfully!')
    print('\n📋 Test credentials:')
    print('   Admin:  admin@paai.org.in  /  Admin@PAAI2024!')
    print('   User:   meera@example.com  /  User@1234!')


if __name__ == "__main__":
    from main import app

    with app.app_context():
        seed()