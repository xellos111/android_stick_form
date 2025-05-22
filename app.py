from flask import Flask, request, render_template, redirect, send_file
import os
import pandas as pd

app = Flask(__name__)
EXCEL_FILE = 'data/submissions.xlsx'
ADMIN_KEY = "mypassword123"  # 관리자 비밀번호

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    user_id = request.form['user_id']
    license_number = request.form['license']

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        if user_id in df['아이디'].astype(str).values:
            return "이미 신청하신 아이디입니다. 한 번만 신청할 수 있습니다.", 400
        if license_number in df['약사면허번호'].astype(str).values:
            return "이미 신청하신 면허번호입니다. 한 번만 신청할 수 있습니다.", 400
    else:
        df = pd.DataFrame()

    data = {
        "번호": len(df) + 1,
        "아이디": user_id,
        "이름": request.form['name'],
        "약사면허번호": license_number,
        "전화번호": request.form['phone'],
        "약국명": request.form['pharmacy'],
        "약국주소": request.form['address']
    }

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    os.makedirs('data', exist_ok=True)
    df.to_excel(EXCEL_FILE, index=False)

    return redirect('/thankyou')  # 완료 페이지로 이동

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')



@app.route('/admin')
def admin():
    key = request.args.get('key')
    if key != ADMIN_KEY:
        return "접근 불가: 비밀번호가 틀렸습니다.", 403

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        return render_template('admin.html', table=df.to_html(index=False))
    else:
        return "아직 신청자가 없습니다."

@app.route('/admin/download')
def download():
    key = request.args.get('key')
    if key != ADMIN_KEY:
        return "접근 불가", 403

    return send_file(EXCEL_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)


