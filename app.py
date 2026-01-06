from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# 📝 ملف تخزين الإعلان
OFFER_FILE = "offer.txt"

def get_current_offer():
    """وظيفة قراءة الإعلان المحفوظ أو عرض نص افتراضي"""
    if os.path.exists(OFFER_FILE):
        try:
            with open(OFFER_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            pass
    return "أهلاً بكم في Ortho_Psy Tech - نحو رقمنة شاملة للممارسة العيادية"

@app.route('/')
def index():
    """الصفحة الرئيسية وتعرض الإعلان المحدث"""
    current_text = get_current_offer()
    return render_template('index.html', offer_text=current_text)

@app.route('/login')
def login():
    """عرض صفحة الدخول (logine.html)"""
    return render_template('logine.html')

@app.route('/login_check', methods=['POST'])
def login_check():
    """التحقق من بيانات الدخول بشكل احترافي من جهة السيرفر 🛡️"""
    user = request.form.get('username')
    pw = request.form.get('password')
    
    # التحقق من البيانات (يمكنك تغييرها لاحقاً أو ربطها بقاعدة بيانات)
    if user == "admin" and pw == "1234":
        return jsonify({"success": True, "redirect": "/dashboard"})
    else:
        return jsonify({"success": False})

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم للإدارة"""
    return render_template('dashboard.html')

@app.route('/update_offer', methods=['POST'])
def update_offer():
    """استقبال التحديثات من لوحة التحكم وحفظها"""
    try:
        new_text = request.form.get('new_offer')
        if new_text:
            with open(OFFER_FILE, "w", encoding="utf-8") as f:
                f.write(new_text)
            return "تم تحديث شريط العروض بنجاح! ✅"
        return "⚠️ النص فارغ", 400
    except Exception as e:
        return f"❌ خطأ في السيرفر: {str(e)}", 500

@app.route('/booking')
def booking():
    """صفحة حجز المواعيد"""
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)
