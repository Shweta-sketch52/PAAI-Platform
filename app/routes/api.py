from flask import Blueprint, request, jsonify, current_app
from app.models import FAQ, ChatSession, ChatMessage
from app.extensions import db, csrf
import uuid, os

api_bp = Blueprint('api', __name__)
csrf.exempt(api_bp)     


# ─── CHATBOT API ─────────────────────────────────────────────────────────────
@api_bp.route('/chat', methods=['POST'])
def chat():
    data       = request.get_json()
    message    = (data.get('message') or '').strip()
    session_id = data.get('session_id') or str(uuid.uuid4())

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    # Get or create chat session
    session = ChatSession.query.filter_by(session_id=session_id).first()
    if not session:
        session = ChatSession(session_id=session_id)
        db.session.add(session)
        db.session.flush()

    # Save user message
    user_msg = ChatMessage(session_id=session.id, role='user', content=message)
    db.session.add(user_msg)

    # Try OpenAI first, fallback to rule-based
    reply = None
    api_key = current_app.config.get('OPENAI_API_KEY', '')
    if api_key and api_key.startswith('sk-'):
        reply = _openai_reply(message, session.id)

    if not reply:
        reply = _rule_based_reply(message)

    # Save bot response
    bot_msg = ChatMessage(session_id=session.id, role='bot', content=reply)
    db.session.add(bot_msg)
    db.session.commit()

    return jsonify({'reply': reply, 'session_id': session_id})


def _openai_reply(message, session_id):
    """Call OpenAI GPT with PAAI system context."""
    try:
        import openai
        history = ChatMessage.query.filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at).limit(10).all()

        messages = [{
            'role': 'system',
            'content': (
                'You are a helpful assistant for PAAI (Patient Advocacy Alliance India), '
                'India\'s leading patient advocacy platform. You help users with: '
                'membership applications, finding resources, understanding programs, '
                'caregiver support, patient rights in India, healthcare navigation, '
                'and connecting with PAAI\'s community. Be empathetic, professional, '
                'and concise. Always encourage users to reach out to PAAI staff for '
                'complex medical or legal advice. PAAI contact: info@paai.org.in, +91 11 2345 6789.'
            )
        }]
        for msg in history[-8:]:
            messages.append({'role': msg.role if msg.role == 'user' else 'assistant', 'content': msg.content})
        messages.append({'role': 'user', 'content': message})

        response = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        current_app.logger.warning(f'OpenAI error: {e}')
        return None


def _rule_based_reply(message):
    """FAQ-based fallback chatbot."""
    msg_lower = message.lower()

    # Check FAQ database
    faqs = FAQ.query.filter_by(is_active=True).all()
    for faq in faqs:
        keywords = [k.strip().lower() for k in (faq.keywords or '').split(',') if k.strip()]
        if any(kw in msg_lower for kw in keywords):
            return faq.answer

    # Built-in rule set
    rules = [
        (['join', 'member', 'membership', 'apply', 'registration'],
         'To join PAAI, visit our Membership page and fill out the application form. '
         'We have three tiers: Individual Advocate, Organizational Member, and Corporate Partner. '
         'Applications are reviewed within 5 business days. 📋'),

        (['program', 'initiative', 'what do you do', 'services'],
         'PAAI runs four flagship programs:\n'
         '1. National Patient Support Network — peer groups in 28 states\n'
         '2. Healthcare Policy Reform Task Force\n'
         '3. Health Literacy & Awareness Campaigns\n'
         '4. Caregiver Training Program\n'
         'Visit our Programs page to learn more!'),

        (['resource', 'guide', 'pdf', 'download', 'handbook'],
         'Our Resource Library has free guides on:\n'
         '• Patient rights under Indian law\n'
         '• Health insurance navigation (PMJAY & private)\n'
         '• Mental wellness for patients & caregivers\n'
         '• Rare disease advocacy\n'
         '• Legal recourse for medical negligence\n'
         'All available for free download on our Resources page.'),

        (['caregiver', 'caring', 'family', 'support', 'help'],
         'PAAI has dedicated support for caregivers! 💚\n'
         'We offer: peer support groups, skills training workshops, '
         'burnout prevention resources, and helpline access. '
         'You can also download our free Caregiver Wellness Guide. '
         'You\'re not alone in this journey.'),

        (['contact', 'phone', 'email', 'address', 'reach'],
         'You can reach PAAI through:\n'
         '📧 info@paai.org.in\n'
         '📞 +91 11 2345 6789\n'
         '📍 C-14, Institutional Area, Lodhi Road, New Delhi – 110 003\n'
         '🕐 Mon–Fri, 9AM–6PM IST'),

        (['event', 'webinar', 'conference', 'workshop', 'upcoming'],
         'We regularly host webinars, conferences, and workshops across India. '
         'Check our News & Events page for upcoming programs. '
         'Members get priority access and early registration!'),

        (['insurance', 'pmjay', 'claim', 'policy', 'health insurance'],
         'Navigating health insurance can be complex. PAAI offers:\n'
         '• Free guide on PMJAY & private insurance claims\n'
         '• Step-by-step appeals toolkit\n'
         '• Helpline for insurance dispute assistance\n'
         'Download our Insurance Navigation Toolkit from the Resources page.'),

        (['rights', 'legal', 'negligence', 'complaint', 'grievance'],
         'Indian patients have important legal rights. PAAI can help you understand:\n'
         '• Clinical Establishments Act provisions\n'
         '• Consumer protection remedies\n'
         '• How to file complaints with State Medical Councils\n'
         '• NHRC complaint process\n'
         'Download our Patient Rights Guide or contact us for assistance.'),

        (['hello', 'hi', 'hey', 'namaste', 'good morning', 'good afternoon'],
         'Hello! 🙏 Welcome to PAAI — Patient Advocacy Alliance India.\n'
         'How can I help you today? I can assist with membership, resources, programs, events, or connect you with our support team.'),

        (['thank', 'thanks', 'dhanyawad'],
         'You\'re most welcome! 🙏 PAAI is here whenever you need support. '
         'Feel free to reach out anytime at info@paai.org.in'),
    ]

    for keywords, response in rules:
        if any(kw in msg_lower for kw in keywords):
            return response

    return ('Thank you for your message. Our team will be happy to help! '
            'For immediate assistance, please:\n'
            '📧 Email: info@paai.org.in\n'
            '📞 Call: +91 11 2345 6789\n'
            'Or visit our Contact page to send us a message.')


# ─── NEWSLETTER ──────────────────────────────────────────────────────────────
@api_bp.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    data  = request.get_json()
    email = (data.get('email') or '').strip()
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email required'}), 400
    # In production: integrate with Mailchimp / SendGrid / your ESP
    return jsonify({'status': 'subscribed', 'email': email})


# ─── STATS (public) ──────────────────────────────────────────────────────────
@api_bp.route('/stats')
def stats():
    from app.models import User, MembershipApplication
    return jsonify({
        'members'  : User.query.filter_by(is_active=True).count(),
        'approved' : MembershipApplication.query.filter_by(status='approved').count(),
    })
