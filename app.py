from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# ✅ رفع سقف حجم البيانات المسموح بها إلى 16 ميجابايت
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 🛠️ الحل الجذري: تحديد المسار المطلق لمجلد المشروع
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 📝 ملفات التخزين بمسارات ثابتة لا تتغير بتغير حالة السيرفر
OFFER_FILE = os.path.join(BASE_DIR, "offer.txt")
BOOKINGS_FILE = os.path.join(BASE_DIR, "bookings.json")
EXAMINEES_FILE = os.path.join(BASE_DIR, "examinees.json")
TOOLS_FILE = os.path.join(BASE_DIR, "tools.json")

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

def get_all_tools():
    if os.path.exists(TOOLS_FILE):
        try:
            with open(TOOLS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except: return []
    return []

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
    if user == "admin" and pw == "1234":
        return jsonify({"success": True, "redirect": "/dashboard"})
    return jsonify({"success": False})

@app.route('/dashboard')
def dashboard():
    bookings = get_all_bookings()
    examinees = get_all_examinees()
    tools = get_all_tools()
    return render_template('dashboard.html', bookings=bookings, examinees=examinees, tools=tools)

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

@app.route('/add_tool', methods=['POST'])
def add_tool():
    try:
        name = request.form.get('tool_name')
        url = request.form.get('tool_url')
        if name and url:
            tools = get_all_tools()
            tool_id = datetime.now().strftime("%Y%m%d%H%M%S")
            tools.append({"id": tool_id, "name": name, "url": url})
            with open(TOOLS_FILE, "w", encoding="utf-8") as f:
                json.dump(tools, f, ensure_ascii=False, indent=4)
            return "تمت إضافة الأداة بنجاح ✅"
        return "بيانات ناقصة", 400
    except Exception as e:
        return str(e), 500

@app.route('/delete_tool/<tool_id>', methods=['POST'])
def delete_tool(tool_id):
    try:
        tools = get_all_tools()
        updated_tools = [t for t in tools if str(t.get('id')) != str(tool_id)]
        with open(TOOLS_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_tools, f, ensure_ascii=False, indent=4)
        return "تم حذف الأداة بنجاح"
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
    app.run(debug=True)
