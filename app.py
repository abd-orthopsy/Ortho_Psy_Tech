from flask import Flask, render_template

app = Flask(__name__)

# 1. مسار الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# 2. مسار صفحة تسجيل دخول الإدارة
@app.route('/login')
def login():
    # ملاحظة: تأكد أن اسم الملف في مجلد templates هو login.html 
    # إذا كان اسم ملفك logine.html فقم بتغييرها هنا
    return render_template('login.html')

# 3. مسار لوحة التحكم (الإدارة الملكية)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 4. مسار صفحة حجز الموعد
@app.route('/booking')
def booking():
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)
