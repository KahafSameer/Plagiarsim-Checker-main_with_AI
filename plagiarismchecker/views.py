
import re
from django.shortcuts import render
from django.http import HttpResponse
from plagiarismchecker.algorithm import main, fileSimilarity
from docx import Document
import PyPDF2
from odf.opendocument import load
from odf.text import P, H
from striprtf.striprtf import rtf_to_text
import logging

logger = logging.getLogger(__name__)

# Template Views
def index(request):
    return render(request, 'pc/index.html')

def index12(request):
    return render(request, 'pc/index12.html')

def compare(request):
    return render(request, 'pc/compare.html')

def fileCompare(request):
    return render(request, 'pc/doc_compare.html')
# Text Compare Page
def highlight_matches(text, matches):
    for match in matches:
        text = re.sub(r'\b({})\b'.format(re.escape(match)), r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)
    return text

def text_compare(request):
    if request.method == 'POST':
        q1 = request.POST.get('q1', '').strip()
        q2 = request.POST.get('q2', '').strip()

        if q1 and q2:
            result, matching_words = fileSimilarity.findFileSimilarity(q1, q2)
            result = round(result, 2)
            
            # Highlight matching words
            q1_highlighted = highlight_matches(q1, matching_words)
            q2_highlighted = highlight_matches(q2, matching_words)

        else:
            result = 0
            q1_highlighted = q1
            q2_highlighted = q2

        return render(request, 'pc/text_compare.html', {
            'result': result,
            'q1': q1_highlighted,
            'q2': q2_highlighted
        })
    
    return render(request, 'pc/text_compare.html')


def file_compare(request):
    if request.method == 'POST':
        try:
            file1 = request.FILES['docfile1']
            file2 = request.FILES['docfile2']

            value1 = extract_text_from_uploaded_file(file1)
            value2 = extract_text_from_uploaded_file(file2)

            result, matching_words = fileSimilarity.findFileSimilarity(value1, value2)
            result = round(result, 2)
            
            # Highlight matching words
            file1_highlighted = highlight_matches(value1, matching_words)
            file2_highlighted = highlight_matches(value2, matching_words)

            return render(request, 'pc/file_compare.html', {
                'result': result,
                'file1_name': file1.name,
                'file2_name': file2.name,
                'file1_content': file1_highlighted,
                'file2_content': file2_highlighted
            })

        except Exception as e:
            logger.error("Error: %s", e)
            return render(request, 'pc/file_compare.html', {'error': 'Failed to read files.'})

    return render(request, 'pc/file_compare.html')
# Web Search (Text)
def test(request):
    if request.method == 'POST':
        q = request.POST.get('q', '').strip()
        if q:
            percent, link, matching_words, matched_text = main.findSimilarity(q)
            percent = round(percent, 2)
            input_text = highlight_matches(q, matching_words)
            matched_text_highlighted = highlight_matches(matched_text, matching_words)
        else:
            percent, link, input_text, matched_text_highlighted = 0, "", q, ""
        
        return render(request, 'pc/index12.html', {
            'link': link,
            'percent': percent,
            'input_text': input_text,
            'matched_text': matched_text_highlighted
        })
    return render(request, 'pc/index12.html')

# Web Search File Upload (.txt, .docx, .pdf, .odt, .rtf)
def filetest(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['docfile']
            value = extract_text_from_uploaded_file(uploaded_file)
            
            percent, link, matching_words, matched_text = main.findSimilarity(value)
            percent = round(percent, 2)
            input_text = highlight_matches(value, matching_words)
            matched_text_highlighted = highlight_matches(matched_text, matching_words)
            
            return render(request, 'pc/index12.html', {
                'link': link,
                'percent': percent,
                'input_text': input_text,
                'matched_text': matched_text_highlighted
            })
        except Exception as e:
            logger.error("File processing error: %s", e)
            return render(request, 'pc/index12.html', {'error': 'Failed to process file.'})
    return render(request, 'pc/index12.html')

# Two Text Input Comparison
def twofiletest1(request):
    q1 = request.POST.get('q1', '').strip()
    q2 = request.POST.get('q2', '').strip()

    if q1 and q2:
        result = fileSimilarity.findFileSimilarity(q1, q2)
        result = round(result, 2)
    else:
        result = 0

    return render(request, 'pc/doc_compare.html', {'result': result})

# Two File Upload Comparison
def twofilecompare1(request):
    try:
        file1 = request.FILES['docfile1']
        file2 = request.FILES['docfile2']

        if file1.size > 5 * 1024 * 1024:
            raise ValueError(f"File '{file1.name}' too large (max 5MB).")
        if file2.size > 5 * 1024 * 1024:
            raise ValueError(f"File '{file2.name}' too large (max 5MB).")

        value1 = extract_text_from_uploaded_file(file1)
        value2 = extract_text_from_uploaded_file(file2)

        result = fileSimilarity.findFileSimilarity(value1, value2)
        result = round(result, 2)

        return render(request, 'pc/doc_compare.html', {
            'result': result,
            'file1_name': file1.name,
            'file2_name': file2.name
        })

    except ValueError as ve:
        return render(request, 'pc/doc_compare.html', {'error': str(ve)})

    except Exception as e:
        logger.error("File read error: %s", e)
        return render(request, 'pc/doc_compare.html', {'error': 'Failed to read one or both files.'})

def extract_text_from_uploaded_file(uploaded_file):
    if uploaded_file.size > 5 * 1024 * 1024:
        raise ValueError("File too large (max 5MB).")
    name = uploaded_file.name.lower()
    text = ''

    if name.endswith('.txt'):
        text = uploaded_file.read().decode('utf-8')
    elif name.endswith('.docx'):
        document = Document(uploaded_file)
        text = ' '.join([para.text for para in document.paragraphs])
    elif name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ''.join([page.extract_text() or '' for page in reader.pages])
    elif name.endswith('.odt'):
        odt_file = load(uploaded_file)
        paragraphs = odt_file.getElementsByType(P) + odt_file.getElementsByType(H)
        text = ' '.join([str(p.firstChild.data) if p.firstChild else '' for p in paragraphs])
    elif name.endswith('.rtf'):
        raw_data = uploaded_file.read().decode('utf-8', errors='ignore')
        text = rtf_to_text(raw_data)
    else:
        raise ValueError("Unsupported file format.")

    return text
