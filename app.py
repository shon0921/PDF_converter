import os
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import fitz  # PyMuPDF
from PyPDF2 import PdfMerger

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    input_pdfs = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ['jpg', 'jpeg', 'png']:
                # 이미지 → PDF 변환
                img = Image.open(save_path).convert('RGB')
                pdf_path = save_path + '.pdf'
                img.save(pdf_path)
                input_pdfs.append(pdf_path)
            elif ext == 'pdf':
                input_pdfs.append(save_path)

    # 병합
    merger = PdfMerger()
    for pdf in input_pdfs:
        merger.append(pdf)

    output_pdf_path = os.path.join(OUTPUT_FOLDER, 'merged_output.pdf')
    merger.write(output_pdf_path)
    merger.close()

    return send_file(output_pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)