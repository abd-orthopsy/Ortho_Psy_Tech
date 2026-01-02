from flask import Flask, render_template

app = Flask(__name__)

# مسار الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# مسار صفحة حجز الموعد الجديد
@app.route('/booking')
def booking():
    return render_template('booking.html')

if __name__ == '__main__':
    app.run(debug=True)
