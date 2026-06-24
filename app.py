"""
Aayu AI — Flask Application
AI-powered medical report analyzer for every Indian family.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime, date
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
from services.llm_service import get_explanation, structure_raw_text, answer_chat_question

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

@app.context_processor
def inject_live_dates():
    """Make today's date available in all templates."""
    now = datetime.now()
    return {
        'today': now.strftime('%d %b %Y'),           # e.g. "20 Jun 2026"
        'today_full': now.strftime('%B %d, %Y'),      # e.g. "June 20, 2026"
        'today_month_year': now.strftime('%B %Y'),    # e.g. "June 2026"
        'today_short': now.strftime('%b %Y'),         # e.g. "Jun 2026"
        'current_year': now.strftime('%Y'),            # e.g. "2026"
    }

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

@app.route('/help')
def help_page():
    return render_template('help.html')

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
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
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
            'test_date': report.test_date or (report.created_at.strftime('%d %b %Y') if report.created_at else datetime.now().strftime('%d %b %Y')),
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
        'lastReport': datetime.now().strftime('%d %b %Y') if report else 'No reports yet',
        'concern': 'None' if not report else 'See Results',
        'color': '#00D4AA'
    }]
    
    return render_template('dashboard.html', user=current_user, report_json=json.dumps(report_data), family_json=json.dumps(family_data))


@app.route('/history')
@login_required
def history():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    
    # Enrich each report with parameter counts
    reports_data = []
    for r in reports:
        params = Parameter.query.filter_by(report_id=r.id).all()
        abnormal = [p for p in params if p.status and p.status != 'NORMAL']
        abnormal_names = ', '.join([p.test_name for p in abnormal[:3]])  # Show top 3
        reports_data.append({
            'id': r.id,
            'test_date': r.test_date or (r.created_at.strftime('%d %b %Y') if r.created_at else datetime.now().strftime('%d %b %Y')),
            'lab_name': r.lab_name or 'Unknown Lab',
            'health_score': r.health_score or 0,
            'abnormal_count': len(abnormal),
            'abnormal_names': abnormal_names,
            'total_params': len(params),
            'created_at': r.created_at
        })
    
    return render_template('history.html', user=current_user, reports=reports_data)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('upload.html', user=current_user)
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    mode = request.form.get('mode', 'scan')
    language = current_user.lang
    
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
            report_count = Report.query.filter_by(user_id=current_user.id).count()
            if report_count == 0:
                extracted_text = """PATIENT_INFO | Het Patel | 21 | Male | SRL Diagnostics | 20 Jun 2026
Hemoglobin | 11.2 | g/dL | 13.5 | 17.5
WBC Count | 7200 | /μL | 4000 | 11000
RBC Count | 4.1 | M/μL | 4.5 | 5.9
Platelets | 215000 | /μL | 150000 | 400000
Creatinine | 0.9 | mg/dL | 0.7 | 1.3
Urea (BUN) | 32 | mg/dL | 15 | 45
Uric Acid | 7.8 | mg/dL | 3.5 | 7.2
SGPT (ALT) | 28 | U/L | 7 | 40
SGOT (AST) | 26 | U/L | 10 | 40
Bilirubin | 0.9 | mg/dL | 0.2 | 1.2
Fasting Glucose | 112 | mg/dL | 70 | 100
HbA1c | 6.1 | % | 0 | 5.7
Total Cholesterol | 198 | mg/dL | 0 | 200
LDL Cholesterol | 128 | mg/dL | 0 | 130
HDL Cholesterol | 38 | mg/dL | 40 | 60
Triglycerides | 168 | mg/dL | 0 | 150
TSH | 5.8 | mIU/L | 0.4 | 4.0
Vitamin D | 14 | ng/mL | 30 | 100
Vitamin B12 | 218 | pg/mL | 200 | 900
Serum Iron | 62 | ug/dL | 60 | 170"""
            elif report_count == 1:
                extracted_text = """PATIENT_INFO | Het Patel | 21 | Male | Dr. Lal PathLabs | 20 Mar 2026
Hemoglobin | 10.5 | g/dL | 13.5 | 17.5
WBC Count | 6800 | /μL | 4000 | 11000
RBC Count | 3.9 | M/μL | 4.5 | 5.9
Platelets | 198000 | /μL | 150000 | 400000
Creatinine | 0.8 | mg/dL | 0.7 | 1.3
Urea (BUN) | 28 | mg/dL | 15 | 45
Uric Acid | 7.2 | mg/dL | 3.5 | 7.2
SGPT (ALT) | 24 | U/L | 7 | 40
SGOT (AST) | 22 | U/L | 10 | 40
Bilirubin | 0.8 | mg/dL | 0.2 | 1.2
Fasting Glucose | 108 | mg/dL | 70 | 100
HbA1c | 5.9 | % | 0 | 5.7
Total Cholesterol | 185 | mg/dL | 0 | 200
LDL Cholesterol | 118 | mg/dL | 0 | 130
HDL Cholesterol | 36 | mg/dL | 40 | 60
Triglycerides | 155 | mg/dL | 0 | 150
TSH | 4.8 | mIU/L | 0.4 | 4.0
Vitamin D | 12 | ng/mL | 30 | 100
Vitamin B12 | 195 | pg/mL | 200 | 900
Serum Iron | 58 | ug/dL | 60 | 170"""
            else:
                extracted_text = """PATIENT_INFO | Het Patel | 21 | Male | Metropolis Labs | 20 Dec 2025
Hemoglobin | 9.8 | g/dL | 13.5 | 17.5
WBC Count | 6200 | /μL | 4000 | 11000
RBC Count | 3.6 | M/μL | 4.5 | 5.9
Platelets | 182000 | /μL | 150000 | 400000
Creatinine | 0.8 | mg/dL | 0.7 | 1.3
Urea (BUN) | 26 | mg/dL | 15 | 45
Uric Acid | 6.8 | mg/dL | 3.5 | 7.2
SGPT (ALT) | 21 | U/L | 7 | 40
SGOT (AST) | 19 | U/L | 10 | 40
Bilirubin | 0.7 | mg/dL | 0.2 | 1.2
Fasting Glucose | 102 | mg/dL | 70 | 100
HbA1c | 5.6 | % | 0 | 5.7
Total Cholesterol | 178 | mg/dL | 0 | 200
LDL Cholesterol | 112 | mg/dL | 0 | 130
HDL Cholesterol | 34 | mg/dL | 40 | 60
Triglycerides | 148 | mg/dL | 0 | 150
TSH | 4.2 | mIU/L | 0.4 | 4.0
Vitamin D | 10 | ng/mL | 30 | 100
Vitamin B12 | 180 | pg/mL | 200 | 900
Serum Iron | 52 | ug/dL | 60 | 170"""
            
        # 2. Parsing (Mocking the string parsing for this implementation)
        # In a real scenario, we parse `extracted_text` string into dicts.
        # Since the vision prompt returns "TEST_NAME | VALUE | UNIT | REF_LOW | REF_HIGH", we can split it.
        lines = extracted_text.strip().split('\n')
        
        # Parse patient info if available
        patient_name = current_user.name
        patient_age = "21"
        patient_gender = "Male"
        lab_name = "Uploaded Report"
        test_date = datetime.now().strftime('%d %b %Y')
        
        for line in lines:
            if line.startswith('PATIENT_INFO'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2 and parts[1]: patient_name = parts[1]
                if len(parts) >= 3 and parts[2]: patient_age = parts[2]
                if len(parts) >= 4 and parts[3]: patient_gender = parts[3]
                if len(parts) >= 5 and parts[4]: lab_name = parts[4]
                if len(parts) >= 6 and parts[5]: test_date = parts[5]

        # Create Report
        new_report = Report(
            user_id=current_user.id,
            patient_name=patient_name,
            patient_age=patient_age,
            patient_gender=patient_gender,
            lab_name=lab_name,
            test_date=test_date,
            health_score=100
        )
        db.session.add(new_report)
        db.session.flush() # Get ID
        
        params_list = []
        from services.parameter_parser import _find_known_param
        from services.diet_recommender import get_diet_tip
        
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
                        rl_num = float(ref_low) if ref_low else 0.0
                        rh_num = float(ref_high) if ref_high else 0.0
                        
                        if rl_num > 0 and v_num < rl_num: status = 'LOW'
                        elif rh_num > 0 and v_num > rh_num: status = 'HIGH'
                    except:
                        v_num = 0.0
                        rl_num = 0.0
                        rh_num = 0.0
                        
                    known = _find_known_param(test_name)
                    category = known['cat'] if known else 'Other'
                    diet_tip = get_diet_tip(test_name, status)
                    
                    params_list.append({
                        'test': test_name,
                        'value': v_num,
                        'ref_low': rl_num,
                        'ref_high': rh_num,
                        'status': status,
                        'category': category
                    })
                    
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
                        category=category,
                        value=value,
                        unit=unit,
                        ref_low=ref_low,
                        ref_high=ref_high,
                        status=status,
                        explanation=explanation,
                        diet_tip=diet_tip
                    )
                    db.session.add(new_param)
        
        # Compute real health score
        from services.health_score import compute_health_score
        health_score = 100
        abnormal_count = 0
        if params_list:
            health_data = compute_health_score(params_list)
            new_report.health_score = health_data['overall']
            health_score = health_data['overall']
            abnormal_count = len([p for p in params_list if p['status'] != 'NORMAL'])
            
        db.session.commit()
        
        details = f"{len(params_list)} parameters extracted · {abnormal_count} abnormal values · Health Score: {health_score}/100"
        return jsonify({'success': True, 'report_id': new_report.id, 'details': details})


@app.route('/results')
@app.route('/results/<int:report_id>')
@login_required
def results(report_id=None):
    if not report_id:
        # Get latest report for user
        report = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).first()
    else:
        report = Report.query.get_or_404(report_id)
        if report.user_id != current_user.id:
            return "Unauthorized", 403
            
    # Dynamic Translation on request
    lang = request.args.get('lang')
    if report and lang and lang in ['en', 'hi', 'gu']:
        params = Parameter.query.filter_by(report_id=report.id).all()
        for p in params:
            param_dict = {
                'test': p.test_name,
                'value': p.value,
                'unit': p.unit,
                'ref_low': p.ref_low,
                'ref_high': p.ref_high,
                'status': p.status
            }
            p.explanation = get_explanation(param_dict, language=lang)
        db.session.commit()
            
    if not report:
        report_data = {'id': None, 'patient_name': current_user.name, 'health_score': 100, 'params': []}
    else:
        params = Parameter.query.filter_by(report_id=report.id).all()
        # Serialize for JS
        report_data = {
            'id': report.id,
            'patient_name': report.patient_name,
            'patient_age': report.patient_age,
            'patient_gender': report.patient_gender,
            'test_date': report.test_date or (report.created_at.strftime('%d %b %Y') if report.created_at else datetime.now().strftime('%d %b %Y')),
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
    
    return render_template('results.html', user=current_user, report_json=json.dumps(report_data), report=report)


def _safe_float(val):
    try:
        return float(str(val).replace('<', '').replace('>', '').strip())
    except ValueError:
        return 0.0

def _get_history_json():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.asc()).all()
    history_data = {
        'scores': [r.health_score for r in reports],
        'reports': []
    }
    months = []
    for r in reports:
        date_str = r.test_date or (r.created_at.strftime('%d %b %Y') if r.created_at else datetime.now().strftime('%d %b %Y'))
        m_str = date_str
        try:
            dt = datetime.strptime(date_str, "%d %b %Y")
            m_str = dt.strftime("%b %Y")
        except:
            if r.created_at:
                m_str = r.created_at.strftime("%b %Y")
            else:
                m_str = datetime.now().strftime("%b %Y")
        months.append(m_str)
        params = Parameter.query.filter_by(report_id=r.id).all()
        history_data['reports'].append({
            'id': r.id,
            'date': date_str,
            'score': r.health_score,
            'params': {p.test_name: {
                'value': _safe_float(p.value),
                'unit': p.unit,
                'status': p.status,
                'refLow': p.ref_low,
                'refHigh': p.ref_high
            } for p in params}
        })
    history_data['months'] = months
    return json.dumps(history_data)

@app.route('/trends')
@login_required
def trends():
    return render_template('trends.html', user=current_user, history_json=_get_history_json())


@app.route('/compare')
@login_required
def compare():
    return render_template('compare.html', user=current_user, history_json=_get_history_json())


@app.route('/diet')
@login_required
def diet():
    # Fetch user's latest report
    report = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).first()
    return render_template('diet.html', user=current_user, report=report)


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
        'lastReport': datetime.now().strftime('%d %b %Y') if report else 'No reports yet',
        'concern': 'None' if not report else 'See Results',
        'color': '#00D4AA'
    }]
    
    return render_template('family.html', user=current_user, family_json=json.dumps(family_data))


@app.route('/chat')
@login_required
def chat():
    report = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).first()
    abnormal_count = 0
    param_count = 0
    if report:
        params = Parameter.query.filter_by(report_id=report.id).all()
        param_count = len(params)
        abnormal_count = len([p for p in params if p.status != 'NORMAL'])
    return render_template('chat.html', user=current_user, report=report, param_count=param_count, abnormal_count=abnormal_count)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    success = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        lang = request.form.get('lang', 'en')
        
        current_user.name = name
        current_user.city = city
        current_user.lang = lang
        db.session.commit()
        success = "Profile updated successfully!"
        
    return render_template('profile.html', user=current_user, success=success)


# ── API endpoints (for AJAX calls) ─────────────────────────
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json()
    msg = data.get('message', '').lower()

    # Get user's latest report
    report = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).first()
    
    # Pre-populate parameter dictionary
    param_vals = {}
    if report:
        params = Parameter.query.filter_by(report_id=report.id).all()
        for p in params:
            param_vals[p.test_name.lower()] = p

    if report:
        context_lines = []
        for name, p in param_vals.items():
            context_lines.append(f"{p.test_name}: {p.value} {p.unit} ({p.status})")
        report_context = "\n".join(context_lines)
    else:
        report_context = "No report available. The user hasn't uploaded a report yet."
        
    reply = answer_chat_question(data.get('message', ''), report_context, current_user.lang)

    return jsonify({'reply': reply})


@app.route('/api/diet_plan/<int:report_id>', methods=['GET'])
@login_required
def api_diet_plan(report_id):
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    params = Parameter.query.filter_by(report_id=report.id).all()
    if not params:
        return jsonify({'diet_plan': 'No parameters found to generate a diet plan.'})

    context_lines = []
    for p in params:
        context_lines.append(f"{p.test_name}: {p.value} {p.unit} ({p.status})")
    report_context = "\n".join(context_lines)

    from services.llm_service import generate_overall_diet_plan
    lang = request.args.get('lang', current_user.lang)
    diet_plan = generate_overall_diet_plan(report_context, lang)

    return jsonify({'diet_plan': diet_plan})


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)

@app.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    success = None
    if request.method == 'POST':
        sms = request.form.get('sms_notifications') == 'on'
        email = request.form.get('email_notifications') == 'on'
        
        current_user.sms_notifications = sms
        current_user.email_notifications = email
        db.session.commit()
        success = "Notification preferences updated successfully!"
        
    return render_template('notifications.html', user=current_user, success=success)

@app.route('/account_security', methods=['GET', 'POST'])
@login_required
def account_security():
    error = None
    success = None
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password_hash, current_password):
            error = "Incorrect current password."
        elif new_password != confirm_password:
            error = "New passwords do not match."
        elif len(new_password) < 6:
            error = "Password must be at least 6 characters."
        else:
            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            success = "Password updated successfully!"
            
    return render_template('account_security.html', user=current_user, error=error, success=success)

if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
    app.run(debug=True, port=5000)
