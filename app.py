from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import base64
from werkzeug.utils import secure_filename

# --- إعدادات رفع الملفات ---
UPLOAD_FOLDER = 'static/uploads'  # المكان الذي ستحفظ فيه الفيديوهات والصور
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'webm'} # السماح بالفيديو

# 🛠️ تحديد المسارات المطلقة لضمان عمل Render بشكل صحيح
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# تحديد الحد الأقصى للحجم بـ 20 ميغا (تم توحيد الحجم ليكون 20 بدلاً من 16 لتجنب التضارب)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 

# دالة للتأكد من وجود مجلد الرفع، وإنشائه إن لم يكن موجوداً
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 🔗 الربط بسحابة MongoDB
MONGO_URI = "mongodb+srv://abdmohamed_db_user:F6S0BtOD5tLkBUop@cluster0.jgimopg.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['ortho_psy_db']

# مجموعات البيانات (Collections)
bookings_col = db['bookings']
examinees_col = db['examinees']
settings_col = db['settings']
slides_col = db['slides']  # ✅ تمت إضافة هذه المجموعة ليعمل السلايدر

# مجموعات الأدوات حسب الأقسام
ortho_tools_col = db['ortho_tools']
psy_tools_col = db['psy_tools']
research_tools_col = db['research_tools']

# --- دالات جلب البيانات الأساسية ---
def get_current_offer():
    offer = settings_col.find_one({"type": "offer"})
    return offer['content'] if offer else "أهلاً بكم في Ortho_Psy Tech"

def get_all_bookings():
    data = list(bookings_col.find().sort("date_submitted", -1))
    for item in data: item['id'] = str(item['_id'])
    return data

def get_all_examinees():
    data = list(examinees_col.find().sort("converted_at", -1))
    for item in data: item['id'] = str(item['_id'])
    return data

def get_tools_from_db(collection):
    data = list(collection.find())
    for item in data: item['id'] = str(item['_id'])
    return data

# --- المسارات الأساسية ---
@app.route('/')
def index():
    current_text = get_current_offer()
    # ✅ إصلاح هام: جلب السلايدات وتمريرها للصفحة
    slides = list(slides_col.find().sort("date", -1))
    return render_template('index.html', offer_text=current_text, slides=slides)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_check', methods=['POST'])
def login_check():
    user = request.form.get('username')
    pw = request.form.get('password')
    
    if user == "admin" and pw == "1234":
        return jsonify({"success": True, "redirect": "/dashboard"})
    elif user == "ortho_admin" and pw == "ortho2026":
        return jsonify({"success": True, "redirect": "/ortho-tech"})
    elif user == "psy_admin" and pw == "psy2026":
        return jsonify({"success": True, "redirect": "/psy-tech"})
    elif user == "research_admin" and pw == "res2026":
        return jsonify({"success": True, "redirect": "/research-tech"})
        
    return jsonify({"success": False})

@app.route('/dashboard')
def dashboard():
    all_bookings = get_all_bookings()
    all_examinees = get_all_examinees()
    # ✅ التأكد من أن الملف المطلوب هو dashboard.html الصحيح
    return render_template('dashboard.html', bookings=all_bookings, examinees=all_examinees)

# --- لوحات تحكم الأقسام التقنية ---
@app.route('/ortho-tech')
def dashboard_ortho():
    tools = get_tools_from_db(ortho_tools_col)
    return render_template('dept_dashboard.html', title="قسم الأرطفونيا Ortho Tech", tools=tools, post_url="/add_ortho_tool", delete_url="/delete_ortho_tool")

@app.route('/psy-tech')
def dashboard_psy():
    tools = get_tools_from_db(psy_tools_col)
    return render_template('dept_dashboard.html', title="قسم علم النفس Psy Tech", tools=tools, post_url="/add_psy_tool", delete_url="/delete_psy_tool")

@app.route('/research-tech')
def dashboard_research():
    tools = get_tools_from_db(research_tools_col)
    return render_template('dept_dashboard.html', title="قسم البحث العلمي Research Tech", tools=tools, post_url="/add_research_tool", delete_url="/delete_research_tool")

# --- دالات إضافة الأدوات ---
def save_tool_to_db(collection):
    try:
        name = request.form.get('tool_name')
        url = request.form.get('tool_url')
        cat = request.form.get('tool_category')
        if name and url and cat:
            collection.insert_one({"name": name, "url": url, "category": cat, "created_at": datetime.now()})
            return "تمت إضافة الأداة بنجاح ✅"
        return "بيانات ناقصة", 400
    except Exception as e: return str(e), 500

@app.route('/add_ortho_tool', methods=['POST'])
def add_ortho_tool(): return save_tool_to_db(ortho_tools_col)

@app.route('/add_psy_tool', methods=['POST'])
def add_psy_tool(): return save_tool_to_db(psy_tools_col)

@app.route('/add_research_tool', methods=['POST'])
def add_research_tool(): return save_tool_to_db(research_tools_col)

# --- دالات حذف الأدوات ---
def delete_tool_from_db(collection, tool_id):
    try:
        collection.delete_one({"_id": ObjectId(tool_id)})
        return "تم الحذف"
    except Exception as e: return str(e), 500

@app.route('/delete_ortho_tool/<tool_id>', methods=['POST'])
def delete_ortho_tool(tool_id): return delete_tool_from_db(ortho_tools_col, tool_id)

@app.route('/delete_psy_tool/<tool_id>', methods=['POST'])
def delete_psy_tool(tool_id): return delete_tool_from_db(psy_tools_col, tool_id)

@app.route('/delete_research_tool/<tool_id>', methods=['POST'])
def delete_research_tool(tool_id): return delete_tool_from_db(research_tools_col, tool_id)

# --- مسارات الحجوزات والمفحوصين ---
@app.route('/save_booking', methods=['POST'])
def save_booking():
    try:
        data = request.json
        data['date_submitted'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        bookings_col.insert_one(data)
        return jsonify({"success": True, "message": "تم تسجيل موعدك بنجاح!"})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

@app.route('/update_offer', methods=['POST'])
def update_offer():
    try:
        new_text = request.form.get('new_offer')
        if new_text is not None:
            settings_col.update_one({"type": "offer"}, {"$set": {"content": new_text}}, upsert=True)
            return "تم التحديث بنجاح! ✅"
        return "المحتوى فارغ", 400
    except Exception as e: return f"خطأ: {str(e)}", 500

@app.route('/convert_to_examinee/<booking_id>', methods=['POST'])
def convert_to_examinee(booking_id):
    try:
        booking = bookings_col.find_one({"_id": ObjectId(booking_id)})
        if booking:
            booking['converted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            examinees_col.insert_one(booking)
            bookings_col.delete_one({"_id": ObjectId(booking_id)})
            return "تم تحويله إلى قائمة المفحوصين ✅"
        return "الموعد غير موجود", 404
    except Exception as e: return str(e), 500

@app.route('/delete_booking/<booking_id>', methods=['POST'])
def delete_booking(booking_id):
    try:
        bookings_col.delete_one({"_id": ObjectId(booking_id)})
        return "تم الحذف"
    except Exception as e: return str(e), 500

@app.route('/delete_examinee/<examinee_id>', methods=['POST'])
def delete_examinee(examinee_id):
    try:
        examinees_col.delete_one({"_id": ObjectId(examinee_id)})
        return "تم حذف ملف المفحوص بنجاح"
    except Exception as e: return str(e), 500

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/examinee_file/<examinee_id>')
def examinee_file(examinee_id):
    try:
        examinee = examinees_col.find_one({"_id": ObjectId(examinee_id)})
        if examinee:
            examinee['id'] = str(examinee['_id'])
            return render_template('examinee_profile.html', e=examinee)
        return "المفحوص غير موجود", 404
    except: return "خطأ في المعرف", 400

@app.route('/save_examinee_note', methods=['POST'])
def save_examinee_note():
    try:
        e_id = request.form.get('id')
        note_type = request.form.get('type')
        content = request.form.get('content')
        examinees_col.update_one({"_id": ObjectId(e_id)}, {"$set": {note_type: content}})
        return jsonify({"success": True})
    except Exception as e: return jsonify({"success": False, "error": str(e)}), 500

@app.route('/save_full_report', methods=['POST'])
def save_full_report():
    try:
        data = request.json
        e_id = data.get('id')
        examinees_col.update_one(
            {"_id": ObjectId(e_id)},
            {"$set": {
                "birth_date": data.get('birth_date'),
                "language_summary": data.get('language_summary'),
                "health_history": data.get('health_history'),
                "tests_results": data.get('tests_results'),
                "goals": data.get('goals'),
                "intervention_plan": data.get('intervention_plan')
            }}
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/follow_up/<examinee_id>')
def follow_up(examinee_id):
    try:
        examinee = examinees_col.find_one({"_id": ObjectId(examinee_id)})
        if examinee:
            examinee['id'] = str(examinee['_id'])
            return render_template('follow_up_report.html', e=examinee)
        return "المفحوص غير موجود", 404
    except Exception as e:
        return f"خطأ في الوصول للتقرير: {str(e)}", 400

@app.route('/upload_examinee_file', methods=['POST'])
def upload_examinee_file():
    try:
        e_id = request.form.get('id')
        file_type = request.form.get('type')
        file = request.files.get('file')
        
        if file:
            encoded_string = base64.b64encode(file.read()).decode('utf-8')
            mime_type = file.content_type
            data_uri = f"data:{mime_type};base64,{encoded_string}"
            
            if file_type == 'photo':
                examinees_col.update_one({"_id": ObjectId(e_id)}, {"$set": {"photo": data_uri}})
            else:
                field = request.form.get('field')
                examinees_col.update_one({"_id": ObjectId(e_id)}, {"$push": {f"{field}_docs": data_uri}})
            
            return jsonify({"success": True, "url": data_uri})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/delete_examinee_photo', methods=['POST'])
def delete_examinee_photo():
    try:
        e_id = request.json.get('id')
        examinees_col.update_one({"_id": ObjectId(e_id)}, {"$unset": {"photo": ""}})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/add_slide', methods=['POST'])
def add_slide():
    # 1. التحقق من وجود الملف
    if 'media_file' not in request.files:
        return 'لا يوجد ملف مرفق', 400
    
    file = request.files['media_file']
    content = request.form.get('content')

    if file.filename == '':
        return 'لم يتم اختيار ملف', 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # حفظ الملف في المجلد
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # المسار للعرض في HTML
        db_file_path = f"/static/uploads/{filename}"

        # ✅ 2. حفظ البيانات في MongoDB (تم تفعيلها الآن)
        slides_col.insert_one({
            "image": db_file_path,  # مسار الفيديو أو الصورة
            "text": content,        # النص المنسق
            "date": datetime.now()
        })

        return 'تم الحفظ بنجاح', 200
    else:
        return 'نوع الملف غير مسموح', 400

# ✅ تم إصلاح الإزاحة (Indentation) هنا ليعمل التطبيق بشكل صحيح
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
