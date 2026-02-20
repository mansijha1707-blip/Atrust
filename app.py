from flask import Flask, render_template, request
import os
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    confidence = None

    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Simulated detection logic (Replace with ML model later)
            score = random.uniform(0, 1)

            if score > 0.6:
                result = "Likely Authentic"
            else:
                result = "Suspicious Content"

            confidence = round(score * 100, 2)

    return render_template('index.html', result=result, confidence=confidence)

if __name__ == '__main__':
    app.run(debug=True)
