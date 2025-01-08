from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import pdfplumber
from pylatexenc.latex2text import LatexNodes2Text
import os
import re
import openai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# summarizer = pipeline("summarization", model="t5-small")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# HELPER FUNCTIONS

def parse_latex(file_path):
    """Parse LaTeX file and extract text using pylatexenc."""
    with open(file_path, 'r', encoding='utf-8') as latex_file:
        latex_content = latex_file.read()
    text = LatexNodes2Text().latex_to_text(latex_content)
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text

# APP ROUTES

@app.route('/upload', methods=['POST'])
def upload_article():
    API_KEY = open("api_key.txt", "r").read()
    openai.api_key = API_KEY

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        if not file.filename.endswith('.tex'):
            os.remove(file_path)
            return jsonify({"error": "Invalid file format. Please upload a .tex file."}), 400

        try:
            text = parse_latex(file_path)
            prompt = "Please summarize this text: " + text
            # summary = summarizer(text, max_length=330, min_length=50, do_sample=False)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = [
                    {"role": "user", "content": prompt}
                ]
            )

            os.remove(file_path)
            # return jsonify({"summary": summary[0]['summary_text']})
            return response
        except Exception as e:
            os.remove(file_path)
            return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
