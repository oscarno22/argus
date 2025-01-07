from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import pdfplumber
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

summarizer = pipeline("summarization", model="t5-small")

def parse_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return " ".join([page.extract_text() for page in pdf.pages])

@app.route('/upload', methods=['POST'])
def upload_article():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:
            text = parse_pdf(file_path)
            summary = summarizer(text, max_length=100, min_length=50, do_sample=False)
            os.remove(file_path)  # Clean up the uploaded file
            return jsonify({"summary": summary[0]['summary_text']})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)