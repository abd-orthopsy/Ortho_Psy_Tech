from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# اسم الملف الذي سيخزن نص الإعلان
OFFER_FILE = "offer.txt"

# دالة مساعدة لقراءة الإعلان المحفوظ
def get_current_offer():
    if os.path.exists(OFFER_FILE):
        with open(OFFER_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "أهلاً بكم في Ortho_Psy Tech - نحو رقمنة شاملة"

# 1. مسار الصفحة الرئيسية
@app.route('/')
def index():
    current_text = get_current_offer()
    return render_template('index.html', offer_text=current_text)

# 2. مسار صفحة تسجيل الدخول
@app.route('/login')
def login():
    # لاحظ: تأكد أن اسم ملفك هو logine.html أو login.html كما سميته في مجلد templates
    return render_template('logine.html')

# 3. مسار لوحة التحكم
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 4. مسار استقبال تحديثات شريط العروض (هنا يتم الربط مع زر لوحة التحكم)
@app.route('/update_offer', methods=['POST'])
def update_offer():
    try:
        # استقبال النص من FormData القادم من الجافا سكريبت
        new_text = request.form.get('new_offer')
        if new_text:
            with open(OFFER_FILE, "w", encoding="utf-8") as f:
                f.write(new_text)
            return "تم تحديث شريط العروض بنجاح!"
        else:
            return "النص فارغ، لم يتم التحديث", 400
    except Exception as e:
        return f"حدث خطأ في السيرفر: {str(e)}", 500

# 5. مسار صفحة حجز الموعد
@app.route('/booking')
def booking():
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)
