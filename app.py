from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from utils.tests import run_test, TEST_DESCRIPTIONS
from collections import namedtuple
import os
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

TestResult = namedtuple('TestResult', ['method', 'statistic', 'pvalue', 'summary'])

def format_result(result, test_type):
    try:
        if hasattr(result, 'statistic') and hasattr(result, 'pvalue'):
            stat = result.statistic
            pval = result.pvalue
        elif isinstance(result, tuple) and len(result) >= 2:
            stat, pval = result[0], result[1]
        else:
            return None
        summary = "有意差あり（p < 0.05）" if pval < 0.05 else "有意差なし（p ≥ 0.05）"
        return TestResult(method=test_type, statistic=round(stat, 4), pvalue=round(pval, 4), summary=summary)
    except Exception:
        return None

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_csv(filepath)
            columns = df.columns.tolist()
            return render_template('index.html',
                                   columns=columns,
                                   df_path=filepath,
                                   test_descriptions=TEST_DESCRIPTIONS,
                                   selected_test="",
                                   selected_col1="",
                                   selected_col2="",
                                   result=None,
                                   formatted=None,
                                   description="")
    return render_template('index.html', columns=[], df_path=None, test_descriptions=TEST_DESCRIPTIONS)

@app.route('/test', methods=['POST'])
def test():
    df_path = request.form.get('df_path')
    if not df_path or not os.path.exists(df_path):
        return redirect(url_for('upload'))

    df = pd.read_csv(df_path)
    columns = df.columns.tolist()

    selected_test = request.form['test_type']
    selected_col1 = request.form.get('col1', '')
    selected_col2 = request.form.get('col2', '')

    result = run_test(df, selected_test, selected_col1, selected_col2)
    formatted = format_result(result, selected_test)
    test_description = TEST_DESCRIPTIONS.get(selected_test, "")

    return render_template('index.html',
                           columns=columns,
                           df_path=df_path,
                           test_descriptions=TEST_DESCRIPTIONS,
                           selected_test=selected_test,
                           selected_col1=selected_col1,
                           selected_col2=selected_col2,
                           result=result,
                           formatted=formatted,
                           description=test_description)

if __name__ == '__main__':
    app.run(debug=True, port=8080)