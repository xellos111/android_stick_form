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
        "우편번호": request.form.get('postcode', ''),
        "약국주소": request.form.get('address', ''),
        "상세주소": request.form.get('address_detail', '')
    }

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

    if "우편번호" in df.columns:
        df["우편번호"] = (
            df["우편번호"]
            .astype(str)                       # 1) 우선 문자열화
            .str.replace(r"\.0$", "", regex=True)  # 2) 끝이 '.0'이면 제거
            .str.zfill(5)
            .str.strip()
        )   
    if "약사면허번호" in df.columns:
        df['약사면허번호'] = df['약사면허번호'].astype(str)
    if "전화번호" in df.columns:
        df['전화번호'] = df['전화번호'].astype(str)

    os.makedirs('data', exist_ok=True)
    df.to_excel(EXCEL_FILE, index=False)

    return redirect('/thankyou')

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
        table_html = df.to_html(index=False, escape=False)
        table_html = table_html.replace('<th>', '<th class="postcode">', 1)
        table_html = table_html.replace('<td>', '<td class="postcode">', 1)

        return render_template('admin.html', table=table_html)
    else:
        return "아직 신청자가 없습니다."

@app.route('/admin/download')
def download():
    key = request.args.get('key')
    if key != ADMIN_KEY:
        return "접근 불가", 403

    return send_file(EXCEL_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
