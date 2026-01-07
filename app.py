from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# ✅ رفع سقف حجم البيانات المسموح بها إلى 16 ميجابايت
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 📝 ملفات التخزين
OFFER_FILE = "offer.txt"
BOOKINGS_FILE = "bookings.json"
EXAMINEES_FILE = "examinees.json" # ملف قاعدة بيانات المفحوصين

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
                return data if isinstance(data, list) else []
        except: return []
    return []

def get_all_examinees():
    """جلب سجل المفحوصين"""
    if os.path.exists(EXAMINEES_FILE):
        try:
            with open(EXAMINEES_FILE, "r", encoding="utf-8") as f:
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
    examinees = get_all_examinees() # جلب قائمة المفحوصين
    return render_template('dashboard.html', bookings=bookings, examinees=examinees)

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
    """تحويل موعد إلى سجل مفحوص دائم"""
    try:
        bookings = get_all_bookings()
        examinees = get_all_examinees()
        
        # البحث عن الموعد المطلوب
        target_booking = next((b for b in bookings if str(b.get('id')) == str(booking_id)), None)
        
        if target_booking:
            # إضافة تاريخ التحويل
            target_booking['converted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            examinees.append(target_booking)
            
            # حذف الموعد من القائمة المؤقتة
            updated_bookings = [b for b in bookings if str(b.get('id')) != str(booking_id)]
            
            # حفظ الملفين
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
    # البحث عن المفحوص المطلوب
    examinee = next((e for e in examinees if str(e.get('id')) == str(examinee_id)), None)
    if examinee:
        return render_template('examinee_profile.html', e=examinee)
    return "المفحوص غير موجود", 404
    
if __name__ == '__main__':
    app.run(debug=True)
