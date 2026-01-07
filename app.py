from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# 📝 ملفات التخزين
OFFER_FILE = "offer.txt"
BOOKINGS_FILE = "bookings.json"

def get_current_offer():
    if os.path.exists(OFFER_FILE):
        try:
            with open(OFFER_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except: pass
    return "أهلاً بكم في Ortho_Psy Tech"

def get_all_bookings():
    if os.path.exists(BOOKINGS_FILE):
        try:
            with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
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
    # جلب المواعيد لعرضها في اللوحة
    bookings = get_all_bookings()
    return render_template('dashboard.html', bookings=all_bookings)

@app.route('/save_booking', methods=['POST'])
def save_booking():
    """استقبال موعد جديد من صفحة booking وحفظه"""
    try:
        data = request.json
        data['id'] = datetime.now().strftime("%Y%m%d%H%M%S") # معرف فريد
        data['date_submitted'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        bookings = get_all_bookings()
        bookings.append(data)
        
        with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(bookings, f, ensure_ascii=False, indent=4)
            
        return jsonify({"success": True, "message": "تم تسجيل موعدك بنجاح! سنتصل بك قريباً."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/update_offer', methods=['POST'])
def update_offer():
    try:
        new_text = request.form.get('new_offer')
        with open(OFFER_FILE, "w", encoding="utf-8") as f:
            f.write(new_text)
        return "تم التحديث بنجاح! ✅"
    except Exception as e:
        return f"خطأ: {str(e)}", 500

@app.route('/booking')
def booking():
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)
