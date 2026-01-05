from flask import Flask, render_template

app = Flask(__name__)

# 1. مسار الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# 2. مسار صفحة تسجيل دخول الإدارة (تم التصحيح هنا)
@app.route('/login')
def login():
    return render_template('login.html')

# 3. مسار صفحة حجز الموعد
@app.route('/booking')
def booking():
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)
