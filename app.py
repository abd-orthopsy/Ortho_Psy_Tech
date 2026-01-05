from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# نص افتراضي لشريط العروض في حال كان الملف فارغاً
offer_file = "offer.txt"

@app.route('/')
def index():
    # قراءة النص من الملف لعرضه في الصفحة الرئيسية
    try:
        with open(offer_file, "r", encoding="utf-8") as f:
            current_offer = f.read()
    except:
        current_offer = "أهلاً بكم في عيادتنا التقنية"
    
    return render_template('index.html', offer_text=current_offer)

@app.route('/login')
def login():
    return render_template('logine.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# المسار الجديد الذي يستقبل التحديثات من لوحة التحكم
@app.route('/update_offer', methods=['POST'])
def update_offer():
    new_text = request.form.get('new_offer')
    if new_text:
        with open(offer_file, "w", encoding="utf-8") as f:
            f.write(new_text)
        return "تم التحديث بنجاح"
    return "خطأ في البيانات", 400

if __name__ == '__main__':
    app.run(debug=True)
