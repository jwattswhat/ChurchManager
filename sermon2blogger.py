"""Convert sermon DOCX content into Blogger-friendly plain text."""

import sys
import os
from docx import Document

def convert_docx_to_text(input_path, output_path):
    doc = Document(input_path)
    output_lines = []

    for para in doc.paragraphs:
        style = para.style.name.lower()
        text = para.text.strip()
        if not text:
            continue

        if "bible quote" in style:
            output_lines.append(f"<blockquote>{text}</blockquote>")
        elif "normal" in style:
            output_lines.append(text + "<br><br>")
        else:
            output_lines.append(text)

    with open(output_path, 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + "\n")

def convert_doc_to_docx(doc_path):
    """Convert .doc to .docx using Word automation (Windows only)"""
    import win32com.client
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(doc_path)
    docx_path = os.path.splitext(doc_path)[0] + ".docx"
    doc.SaveAs(docx_path, FileFormat=16)  # 16 = wdFormatXMLDocument
    doc.Close()
    word.Quit()
    return docx_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sermon2python.py filename.docx|.doc")
        sys.exit(1)

    filename = sys.argv[1]
    sermons_dir = os.path.join(os.getcwd(), "sermons")
    input_file = os.path.join(sermons_dir, filename)

    if not (input_file.lower().endswith(".docx") or input_file.lower().endswith(".doc")) or not os.path.exists(input_file):
        print(f"Error: File '{filename}' not found in 'sermons' folder.")
        sys.exit(1)

    # Convert .doc to .docx if needed
    if input_file.lower().endswith(".doc"):
        try:
            print("Converting .doc to .docx...")
            input_file = convert_doc_to_docx(input_file)
        except Exception as e:
            print(f"Error converting .doc to .docx: {e}")
            sys.exit(1)

    output_file = os.path.splitext(input_file)[0] + ".txt"
    convert_docx_to_text(input_file, output_file)
    print(f"Converted: {output_file}")
