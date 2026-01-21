from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

# 🛠️ تحديد المسارات المطلقة لضمان عمل Render بشكل صحيح
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# ✅ رفع سقف حجم البيانات المسموح بها إلى 16 ميجابايت
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 📝 ملفات التخزين الأساسية (الإدارة الملكية) باستخدام المسار المطلق
OFFER_FILE = os.path.join(BASE_DIR, "offer.txt")
BOOKINGS_FILE = os.path.join(BASE_DIR, "bookings.json")
EXAMINEES_FILE = os.path.join(BASE_DIR, "examinees.json")

# 📂 ملفات تخزين الأدوات حسب الأقسام (النظام الجديد)
ORTHO_TOOLS_FILE = os.path.join(BASE_DIR, "ortho_tools.json")
PSY_TOOLS_FILE = os.path.join(BASE_DIR, "psy_tools.json")
RESEARCH_TOOLS_FILE = os.path.join(BASE_DIR, "research_tools.json")

# --- دالات جلب البيانات الأساسية ---
def get_current_offer():
    if os.path.exists(OFFER_FILE):
        try:
            with open(OFFER_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return content if content else "أهلاً بكم في Ortho_Psy Tech"
        except: pass
    return "أهلاً بكم في Ortho_Psy Tech"

def get_all_bookings():
    if os.path.exists(BOOKINGS_FILE):
        try:
            with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return sorted(data, key=lambda x: x.get('date_submitted', ''), reverse=True)
                return []
        except: return []
    return []

def get_all_examinees():
    if os.path.exists(EXAMINEES_FILE):
        try:
            with open(EXAMINEES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return sorted(data, key=lambda x: x.get('converted_at', ''), reverse=True)
                return []
        except: return []
    return []

# --- دالات جلب أدوات الأقسام ---
def get_tools_by_file(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except: return []
    return []

# --- المسارات الأساسية ---
@app.route('/')
def index():
    current_text = get_current_offer()
    return render_template('index.html', offer_text=current_text)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_check', methods=['POST'])
def login_check():
    user = request.form.get('username')
    pw = request.form.get('password')
    
    # 1. الإدارة الملكية
    if user == "admin" and pw == "1234":
        return jsonify({"success": True, "redirect": "/dashboard"})
    # 2. قسم الأرطفونيا
    elif user == "ortho_admin" and pw == "ortho2026":
        return jsonify({"success": True, "redirect": "/dashboard_ortho"})
    # 3. قسم العيادي
    elif user == "psy_admin" and pw == "psy2026":
        return jsonify({"success": True, "redirect": "/dashboard_psy"})
    # 4. قسم البحث
    elif user == "research_admin" and pw == "res2026":
        return jsonify({"success": True, "redirect": "/dashboard_research"})
        
    return jsonify({"success": False})

# --- لوحة تحكم الإدارة الملكية (تستخدم dashboard.html الأصلي) ---
@app.route('/dashboard')
def dashboard():
    bookings = get_all_bookings()
    examinees = get_all_examinees()
    # هنا الإدارة العامة تبقى كما هي بدون تغيير is_dept
    return render_template('dashboard.html', bookings=bookings, examinees=examinees)

# --- لوحات تحكم الأقسام التقنية (تستخدم dept_dashboard.html حصراً) ---
@app.route('/ortho-tech')
def dashboard_ortho():
    tools = get_tools_by_file(ORTHO_TOOLS_FILE)
    return render_template('dept_dashboard.html', title="قسم الأرطفونيا Ortho Tech", tools=tools, post_url="/add_ortho_tool", delete_url="/delete_ortho_tool")

@app.route('/psy-tech')
def dashboard_psy():
    tools = get_tools_by_file(PSY_TOOLS_FILE)
    return render_template('dept_dashboard.html', title="قسم علم النفس Psy Tech", tools=tools, post_url="/add_psy_tool", delete_url="/delete_psy_tool")

@app.route('/research-tech')
def dashboard_research():
    tools = get_tools_by_file(RESEARCH_TOOLS_FILE)
    return render_template('dept_dashboard.html', title="قسم البحث العلمي Research Tech", tools=tools, post_url="/add_research_tool", delete_url="/delete_research_tool")

# --- دالات إضافة الأدوات ---
def save_tool_to_dept(file_path):
    try:
        name = request.form.get('tool_name')
        url = request.form.get('tool_url')
        cat = request.form.get('tool_category')
        if name and url and cat:
            tools = get_tools_by_file(file_path)
            tool_id = datetime.now().strftime("%Y%m%d%H%M%S")
            tools.append({"id": tool_id, "name": name, "url": url, "category": cat})
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(tools, f, ensure_ascii=False, indent=4)
            return "تمت إضافة الأداة بنجاح ✅"
        return "بيانات ناقصة", 400
    except Exception as e:
        return str(e), 500

@app.route('/add_ortho_tool', methods=['POST'])
def add_ortho_tool(): return save_tool_to_dept(ORTHO_TOOLS_FILE)

@app.route('/add_psy_tool', methods=['POST'])
def add_psy_tool(): return save_tool_to_dept(PSY_TOOLS_FILE)

@app.route('/add_research_tool', methods=['POST'])
def add_research_tool(): return save_tool_to_dept(RESEARCH_TOOLS_FILE)

# --- دالات حذف الأدوات ---
def delete_tool_from_dept(file_path, tool_id):
    try:
        tools = get_tools_by_file(file_path)
        updated = [t for t in tools if str(t.get('id')) != str(tool_id)]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(updated, f, ensure_ascii=False, indent=4)
        return "تم الحذف"
    except Exception as e: return str(e), 500

@app.route('/delete_ortho_tool/<tool_id>', methods=['POST'])
def delete_ortho_tool(tool_id): return delete_tool_from_dept(ORTHO_TOOLS_FILE, tool_id)

@app.route('/delete_psy_tool/<tool_id>', methods=['POST'])
def delete_psy_tool(tool_id): return delete_tool_from_dept(PSY_TOOLS_FILE, tool_id)

@app.route('/delete_research_tool/<tool_id>', methods=['POST'])
def delete_research_tool(tool_id): return delete_tool_from_dept(RESEARCH_TOOLS_FILE, tool_id)

# --- مسارات الحجوزات والمفحوصين (الأصلية كما هي) ---
@app.route('/save_booking', methods=['POST'])
def save_booking():
    try:
        data = request.json
        data['id'] = datetime.now().strftime("%Y%m%d%H%M%S") 
        data['date_submitted'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        bookings = get_all_bookings()
        bookings.append(data)
        with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(bookings, f, ensure_ascii=False, indent=4)
        return jsonify({"success": True, "message": "تم تسجيل موعدك بنجاح!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/update_offer', methods=['POST'])
def update_offer():
    try:
        new_text = request.form.get('new_offer')
        if new_text is not None:
            with open(OFFER_FILE, "w", encoding="utf-8") as f:
                f.write(new_text)
            return "تم التحديث بنجاح! ✅"
        return "المحتوى فارغ", 400
    except Exception as e:
        return f"خطأ: {str(e)}", 500

@app.route('/convert_to_examinee/<booking_id>', methods=['POST'])
def convert_to_examinee(booking_id):
    try:
        bookings = get_all_bookings()
        examinees = get_all_examinees()
        target_booking = next((b for b in bookings if str(b.get('id')) == str(booking_id)), None)
        if target_booking:
            target_booking['converted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            examinees.append(target_booking)
            updated_bookings = [b for b in bookings if str(b.get('id')) != str(booking_id)]
            with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(updated_bookings, f, ensure_ascii=False, indent=4)
            with open(EXAMINEES_FILE, "w", encoding="utf-8") as f:
                json.dump(examinees, f, ensure_ascii=False, indent=4)
            return "تم تحويله إلى قائمة المفحوصين ✅"
        return "الموعد غير موجود", 404
    except Exception as e:
        return str(e), 500

@app.route('/delete_booking/<booking_id>', methods=['POST'])
def delete_booking(booking_id):
    try:
        bookings = get_all_bookings()
        updated_bookings = [b for b in bookings if str(b.get('id')) != str(booking_id)]
        with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_bookings, f, ensure_ascii=False, indent=4)
        return "تم الحذف"
    except Exception as e:
        return str(e), 500

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/examinee_file/<examinee_id>')
def examinee_file(examinee_id):
    examinees = get_all_examinees()
    examinee = next((e for e in examinees if str(e.get('id')) == str(examinee_id)), None)
    if examinee:
        return render_template('examinee_profile.html', e=examinee)
    return "المفحوص غير موجود", 404
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
