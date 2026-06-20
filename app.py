"""
Aayu AI — Flask Application
AI-powered medical report analyzer for every Indian family.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from database_models import db, User, Report, Parameter

# Import AI Services
from services.vision_extractor import extract_text_from_photo
from services.pdf_extractor import extract_text_from_pdf
from services.ocr_extractor import extract_text_from_image
from services.llm_service import get_explanation, structure_raw_text

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'aayu-ai-dev-secret-key-2026')

# ── Database Configuration ─────────────────────────────────
# Default to SQLite if DATABASE_URL is not set
default_db_url = 'sqlite:///aayu.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db_url)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload Config
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

db.init_app(app)

# ── Login Manager Configuration ────────────────────────────
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


# ── Public Routes ──────────────────────────────────────────
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    return render_template('landing.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/security')
def security():
    return render_template('security.html')


# ── Auth Routes ────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('upload'))
            
        return render_template('auth/login.html', error='Invalid email or password')
    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        city = request.form.get('city', '').strip()
        lang = request.form.get('lang', 'en')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('auth/register.html', error='Email already registered')

        hashed_password = generate_password_hash(password)
        
        new_user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            city=city,
            lang=lang
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('upload'))
        
    return render_template('auth/register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ── App Routes (require login) ─────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    report = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).first()
    
    if not report:
        # Pass empty data if no reports
        report_data = {'id': None, 'patient_name': current_user.name, 'health_score': 100, 'params': []}
    else:
        params = Parameter.query.filter_by(report_id=report.id).all()
        report_data = {
            'id': report.id,
            'patient_name': report.patient_name,
            'test_date': report.test_date,
            'lab_name': report.lab_name,
            'health_score': report.health_score,
            'params': [{
                'id': p.id,
                'test': p.test_name,
                'cat': p.category,
                'value': p.value,
                'unit': p.unit,
                'refLow': p.ref_low,
                'refHigh': p.ref_high,
                'status': p.status,
                'explanation': p.explanation,
                'diet': p.diet_tip
            } for p in params]
        }
    
    family_data = [{
        'id': current_user.id,
        'name': current_user.name,
        'initial': current_user.name[0].upper() if current_user.name else 'U',
        'age': report.patient_age if report and getattr(report, 'patient_age', None) else '--',
        'gender': report.patient_gender if report and getattr(report, 'patient_gender', None) else 'Unknown',
        'score': report.health_score if report else 100,
        'reports': Report.query.filter_by(user_id=current_user.id).count(),
        'lastReport': report.test_date if report else 'No reports yet',
        'concern': 'None' if not report else 'See Results',
        'color': '#00D4AA'
    }]
    
    return render_template('dashboard.html', user=current_user, report_json=json.dumps(report_data), family_json=json.dumps(family_data))


@app.route('/history')
@login_required
def history():
    return render_template('history.html', user=current_user)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('upload.html', user=current_user)
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    mode = request.form.get('mode', 'phone')
    language = request.form.get('lang', 'en')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 1. Extraction
        extracted_text = ""
        if mode == 'pdf' and filename.lower().endswith('.pdf'):
            raw_text = extract_text_from_pdf(filepath)
            extracted_text = structure_raw_text(raw_text)
        elif mode == 'scan':
            raw_text = extract_text_from_image(filepath)
            extracted_text = structure_raw_text(raw_text)
        else: # phone / fallback
            extracted_text = extract_text_from_photo(filepath)
            
        # Clean up file
        try:
            os.remove(filepath)
        except:
            pass
            
        if not extracted_text:
            return jsonify({'error': 'Failed to extract text from the document.'}), 500
            
        # 2. Parsing (Mocking the string parsing for this implementation)
        # In a real scenario, we parse `extracted_text` string into dicts.
        # Since the vision prompt returns "TEST_NAME | VALUE | UNIT | REF_LOW | REF_HIGH", we can split it.
        lines = extracted_text.strip().split('\n')
        
        # Create Report
        new_report = Report(
            user_id=current_user.id,
            patient_name=current_user.name,
            test_date="Recent",
            lab_name="Uploaded Report",
            health_score=85 # Default, will calculate
        )
        db.session.add(new_report)
        db.session.flush() # Get ID
        
        total_score = 100
        abnormal_count = 0
        
        for line in lines:
            if '|' in line and not line.startswith('PATIENT_INFO') and not line.startswith('TEST_NAME'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    test_name = parts[0]
                    value = parts[1]
                    unit = parts[2]
                    ref_low = parts[3] if len(parts) > 3 else ''
                    ref_high = parts[4] if len(parts) > 4 else ''
                    
                    # Basic status logic
                    status = 'NORMAL'
                    try:
                        v_num = float(value.replace('<','').replace('>','').strip())
                        if ref_low and ref_high:
                            if v_num < float(ref_low): status = 'LOW'
                            elif v_num > float(ref_high): status = 'HIGH'
                    except:
                        pass
                        
                    if status != 'NORMAL':
                        total_score -= 5
                        abnormal_count += 1
                        
                    param_dict = {
                        'test': test_name,
                        'value': value,
                        'unit': unit,
                        'ref_low': ref_low,
                        'ref_high': ref_high,
                        'status': status
                    }
                    
                    # 3. LLM Explanation
                    explanation = get_explanation(param_dict, language=language)
                    
                    new_param = Parameter(
                        report_id=new_report.id,
                        test_name=test_name,
                        value=value,
                        unit=unit,
                        ref_low=ref_low,
                        ref_high=ref_high,
                        status=status,
                        explanation=explanation,
                        diet_tip="Consult doctor for specific diet." if status != 'NORMAL' else ""
                    )
                    db.session.add(new_param)
        
        new_report.health_score = max(0, total_score)
        db.session.commit()
        
        return jsonify({'success': True, 'report_id': new_report.id})


@app.route('/results')
@app.route('/results/<int:report_id>')
@login_required
def results(report_id=None):
    if not report_id:
        # Get latest report for user
        report = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).first()
        if not report:
            return redirect(url_for('upload'))
        report_id = report.id
    else:
        report = Report.query.get_or_404(report_id)
        if report.user_id != current_user.id:
            return "Unauthorized", 403
            
    params = Parameter.query.filter_by(report_id=report.id).all()
    
    # Serialize for JS
    report_data = {
        'id': report.id,
        'patient_name': report.patient_name,
        'test_date': report.test_date,
        'lab_name': report.lab_name,
        'health_score': report.health_score,
        'params': [{
            'id': p.id,
            'test': p.test_name,
            'cat': p.category,
            'value': p.value,
            'unit': p.unit,
            'refLow': p.ref_low,
            'refHigh': p.ref_high,
            'status': p.status,
            'explanation': p.explanation,
            'diet': p.diet_tip
        } for p in params]
    }
    
    return render_template('results.html', user=current_user, report_json=json.dumps(report_data))


def _get_history_json():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.asc()).all()
    history_data = {
        'months': [r.test_date for r in reports],
        'scores': [r.health_score for r in reports],
        'reports': []
    }
    for r in reports:
        params = Parameter.query.filter_by(report_id=r.id).all()
        history_data['reports'].append({
            'id': r.id,
            'date': r.test_date,
            'score': r.health_score,
            'params': {p.test_name: {
                'value': float(p.value.replace('<', '').replace('>', '')) if p.value.replace('.', '').replace('<', '').replace('>', '').isdigit() else 0,
                'unit': p.unit,
                'status': p.status,
                'refLow': p.ref_low,
                'refHigh': p.ref_high
            } for p in params}
        })
    return json.dumps(history_data)

@app.route('/trends')
@login_required
def trends():
    return render_template('trends.html', user=current_user, history_json=_get_history_json())


@app.route('/compare')
@login_required
def compare():
    return render_template('compare.html', user=current_user, history_json=_get_history_json())


@app.route('/family')
@login_required
def family():
    # Fetch user's latest report to show stats
    report = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).first()
    
    family_data = [{
        'id': current_user.id,
        'name': current_user.name,
        'initial': current_user.name[0].upper() if current_user.name else 'U',
        'age': report.patient_age if report and report.patient_age else '--',
        'gender': report.patient_gender if report and report.patient_gender else 'Unknown',
        'score': report.health_score if report else 0,
        'reports': Report.query.filter_by(user_id=current_user.id).count(),
        'lastReport': report.test_date if report else 'No reports yet',
        'concern': 'None' if not report else 'See Results',
        'color': '#00D4AA'
    }]
    
    return render_template('family.html', user=current_user, family_json=json.dumps(family_data))


@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=current_user)


# ── API endpoints (for AJAX calls) ─────────────────────────
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json()
    msg = data.get('message', '').lower()

    responses = {
        'hemoglobin': 'Your hemoglobin (11.2 g/dL) is below normal (13.5-17.5), indicating mild iron-deficiency anemia. Your trend shows improvement from 10.5 in January. Keep eating palak, rajma, and pomegranate. Follow-up test in 3 months recommended.',
        'glucose': 'Your fasting glucose (112) and HbA1c (6.1%) are both in the prediabetes range — early warning, not diabetes yet. It is fully reversible: cut refined carbs, add 30 min daily walking, avoid sugary drinks. Retest HbA1c in 3 months.',
        'tsh': 'Your TSH (5.8 mIU/L) is above normal (0.4-4.0), suggesting hypothyroidism. Symptoms: fatigue, weight gain, feeling cold, hair thinning. See an Endocrinologist — thyroxine is a simple daily tablet that normalizes this completely.',
        'vitamin': 'Vitamin D at 14 ng/mL is clearly deficient (normal: 30-100). 20 min of morning sunlight daily helps, but at this level a Vitamin D3 supplement is typically needed. Ask your doctor about a 60,000 IU weekly course for 8 weeks.',
        'uric': 'Uric acid at 7.8 mg/dL increases your gout risk. Cut red meat, organ meats, and drink 3+ litres water daily. Cherries and low-fat dairy help lower uric acid naturally. Retest in 6 weeks after dietary changes.',
    }

    reply = 'Based on your July 2024 report I can see 9 abnormal values across Blood, Glucose, Thyroid, Lipid, and Vitamins panels. What would you like to understand better?'
    for key, response in responses.items():
        if key in msg:
            reply = response
            break

    return jsonify({'reply': reply})


if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
    app.run(debug=True, port=5000)
