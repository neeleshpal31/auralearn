import io
import zlib
import re

def escape_pdf_text(text):
    """Escape special characters for PDF text literal syntax."""
    if text is None:
        return ""
    text = str(text)
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def generate_certificate_pdf(certificate_data):
    """
    Generates an ultra-luxurious, official 1-page Landscape A4 PDF certificate
    using 100% pure Python standard library (NO external pip dependencies required).
    """
    student_name = certificate_data.get('student_name', 'Student Learner')
    course_title = certificate_data.get('course_title', 'Mastery Course')
    category = certificate_data.get('course_category', 'Computer Science')
    level = certificate_data.get('course_skill_level', 'Intermediate')
    score = certificate_data.get('exam_score', 95)
    grade = certificate_data.get('grade', 'A+')
    grade_title = certificate_data.get('grade_title', 'Distinction (Honors)')
    cert_code = certificate_data.get('certificate_code', 'AL-CERT-2026-X')
    issued_date = certificate_data.get('issued_date', 'October 02, 2026')

    # Dimensions for A4 Landscape (in PDF points, 72 pt = 1 inch)
    # A4 = 841.89 x 595.28 pt (~ 297mm x 210mm)
    w = 841.89
    h = 595.28

    # Build PDF graphics content stream
    ops = []
    
    # 1. Background Fill (Midnight Slate)
    ops.append("q")
    ops.append("0.031 0.051 0.102 rg") # #080d1a
    ops.append(f"0 0 {w:.2f} {h:.2f} re f")
    
    # 2. Outer Gold Border
    ops.append("0.984 0.749 0.141 RG") # #fbbf24
    ops.append("3.5 w")
    ops.append(f"16 16 {w-32:.2f} {h-32:.2f} re S")
    
    # 3. Inner Fine Gold Border
    ops.append("0.851 0.467 0.024 RG") # #d97706
    ops.append("1.0 w")
    ops.append(f"24 24 {w-48:.2f} {h-48:.2f} re S")
    
    # 4. Subtle Inner Card Background
    ops.append("0.051 0.082 0.153 rg") # #0d1527
    ops.append(f"28 28 {w-56:.2f} {h-56:.2f} re f")
    
    # 5. Header Branding Divider Line
    ops.append("0.118 0.161 0.231 RG") # #1e293b
    ops.append("1.0 w")
    ops.append(f"48 {h-68:.2f} m {w-48:.2f} {h-68:.2f} l S")
    
    # 6. Metadata Banner Box
    banner_w = 540
    banner_h = 28
    banner_x = (w - banner_w) / 2.0
    banner_y = h - 315
    ops.append("0.031 0.051 0.102 rg")
    ops.append(f"{banner_x:.2f} {banner_y:.2f} {banner_w:.2f} {banner_h:.2f} re f")
    ops.append("0.118 0.161 0.231 RG")
    ops.append(f"{banner_x:.2f} {banner_y:.2f} {banner_w:.2f} {banner_h:.2f} re S")

    # 7. Signature Lines
    # Left Signature Line
    ops.append("0.984 0.749 0.141 RG")
    ops.append(f"80 {h-395:.2f} m 240 {h-395:.2f} l S")
    # Right Signature Line
    ops.append(f"{w-240:.2f} {h-395:.2f} m {w-80:.2f} {h-395:.2f} l S")

    # 8. Bottom Verification Divider
    ops.append("0.118 0.161 0.231 RG")
    ops.append(f"48 55 m {w-48:.2f} 55 l S")

    # 9. Gold Official Seal Shapes
    seal_cx = w / 2.0
    seal_cy = h - 395
    # Outer gold circle approximation or square disc
    ops.append("0.851 0.467 0.024 rg")
    ops.append("0.996 0.878 0.278 RG")
    ops.append("2.0 w")
    # Octagon seal
    r = 38.0
    ops.append(f"{seal_cx-r+11:.2f} {seal_cy-r:.2f} m "
               f"{seal_cx+r-11:.2f} {seal_cy-r:.2f} l "
               f"{seal_cx+r:.2f} {seal_cy-r+11:.2f} l "
               f"{seal_cx+r:.2f} {seal_cy+r-11:.2f} l "
               f"{seal_cx+r-11:.2f} {seal_cy+r:.2f} l "
               f"{seal_cx-r+11:.2f} {seal_cy+r:.2f} l "
               f"{seal_cx-r:.2f} {seal_cy+r-11:.2f} l "
               f"{seal_cx-r:.2f} {seal_cy-r+11:.2f} l h B")
    
    # Inner dark disc
    ops.append("0.471 0.208 0.059 rg")
    ri = 28.0
    ops.append(f"{seal_cx-ri:.2f} {seal_cy-ri:.2f} {ri*2:.2f} {ri*2:.2f} re f")

    ops.append("Q") # restore graphics state

    # Text Elements (Typography)
    def text_obj(font, size, r, g, b, x, y, text_str, align='center'):
        clean_text = escape_pdf_text(text_str)
        # Approximate char width for centering
        char_w = size * 0.52
        if font == '/F1': # Helvetica-Bold
            char_w = size * 0.58
        elif font == '/F3': # Times-Italic
            char_w = size * 0.48
            
        str_len = len(text_str) * char_w
        if align == 'center':
            tx = x - (str_len / 2.0)
        elif align == 'right':
            tx = x - str_len
        else:
            tx = x
            
        return f"BT {r:.3f} {g:.3f} {b:.3f} rg {font} {size:.1f} Tf 1 0 0 1 {tx:.2f} {y:.2f} Tm ({clean_text}) Tj ET"

    text_ops = []
    
    # Header Brand
    text_ops.append(text_obj('/F1', 14, 0.984, 0.749, 0.141, 48, h - 58, "AuraLearn Academy", align='left'))
    text_ops.append(text_obj('/F1', 8, 0.580, 0.639, 0.722, w - 48, h - 56, "HONORIS ACADEMIA  |  VERIFIED CREDENTIAL", align='right'))

    # Title & Subtitle
    text_ops.append(text_obj('/F1', 20, 1.0, 1.0, 1.0, w / 2.0, h - 105, "CERTIFICATE OF COMPLETION & MASTERY"))
    text_ops.append(text_obj('/F1', 9, 0.984, 0.749, 0.141, w / 2.0, h - 124, "THIS OFFICIAL CREDENTIAL IS PROUDLY AWARDED TO"))

    # Recipient Name (Prominent Gold)
    text_ops.append(text_obj('/F1', 30, 0.996, 0.878, 0.278, w / 2.0, h - 170, student_name))

    # Accomplishment Statements
    text_ops.append(text_obj('/F2', 10, 0.580, 0.639, 0.722, w / 2.0, h - 208, "For successfully completing all interactive syllabi, mastering foundational and advanced curriculum,"))
    text_ops.append(text_obj('/F2', 10, 0.580, 0.639, 0.722, w / 2.0, h - 225, "and demonstrating academic excellence in the proctored final examination for"))

    # Course Name (Bold White)
    text_ops.append(text_obj('/F1', 20, 1.0, 1.0, 1.0, w / 2.0, h - 262, course_title))

    # Meta Tags Banner Info
    banner_text = f"Category: {category}   |   Level: {level}   |   Exam Score: {score}%   |   Grade: {grade} ({grade_title})"
    text_ops.append(text_obj('/F1', 9, 0.796, 0.835, 0.882, w / 2.0, banner_y + 9, banner_text))

    # Signatures
    # Left Signature
    text_ops.append(text_obj('/F3', 18, 0.984, 0.749, 0.141, 160, h - 386, "Dr. Evelyn Vance"))
    text_ops.append(text_obj('/F1', 9, 1.0, 1.0, 1.0, 160, h - 408, "Dr. Evelyn Vance, Ph.D."))
    text_ops.append(text_obj('/F2', 7.5, 0.580, 0.639, 0.722, 160, h - 420, "Director of Academic Excellence"))

    # Center Seal Text
    text_ops.append(text_obj('/F1', 6.5, 0.996, 0.878, 0.278, seal_cx, seal_cy + 12, "OFFICIAL SEAL"))
    text_ops.append(text_obj('/F1', 8.5, 1.0, 1.0, 1.0, seal_cx, seal_cy - 1, "VERIFIED"))
    text_ops.append(text_obj('/F1', 7.0, 0.996, 0.878, 0.278, seal_cx, seal_cy - 14, "2026"))

    # Right Signature
    text_ops.append(text_obj('/F3', 18, 0.984, 0.749, 0.141, w - 160, h - 386, "AuraLearn Academic Board"))
    text_ops.append(text_obj('/F1', 9, 1.0, 1.0, 1.0, w - 160, h - 408, "AuraLearn Certification Council"))
    text_ops.append(text_obj('/F2', 7.5, 0.580, 0.639, 0.722, w - 160, h - 420, f"Issued: {issued_date}"))

    # Bottom Verification Bar
    text_ops.append(text_obj('/F1', 7.5, 0.392, 0.455, 0.545, 48, 40, f"Certificate ID: {cert_code}", align='left'))
    text_ops.append(text_obj('/F1', 7.5, 0.392, 0.455, 0.545, w - 48, 40, f"Verify: aurademi.edu/certificate/{cert_code}", align='right'))

    content_stream = "\n".join(ops + text_ops).encode('latin1', 'replace')
    compressed_stream = zlib.compress(content_stream)

    # Build standard PDF-1.4 file
    objects = []
    
    # 1: Catalog
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    
    # 2: Pages
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    
    # 3: Page (Landscape A4)
    objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w:.2f} {h:.2f}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R /F3 7 0 R >> >> >>".encode('ascii'))
    
    # 4: Contents Stream
    objects.append(f"<< /Length {len(compressed_stream)} /Filter /FlateDecode >>\nstream\n".encode('ascii') + compressed_stream + b"\nendstream")
    
    # 5: Font F1 (Helvetica-Bold)
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    
    # 6: Font F2 (Helvetica)
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    
    # 7: Font F3 (Times-Italic)
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Italic /Encoding /WinAnsiEncoding >>")

    # Assemble PDF with XRef Table
    pdf_out = bytearray()
    pdf_out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf_out))
        pdf_out.extend(f"{i} 0 obj\n".encode('ascii'))
        pdf_out.extend(obj)
        pdf_out.extend(b"\nendobj\n")
        
    xref_offset = len(pdf_out)
    pdf_out.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode('ascii'))
    for off in offsets[1:]:
        pdf_out.extend(f"{off:010d} 00000 n \n".encode('ascii'))
        
    pdf_out.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode('ascii'))

    buffer = io.BytesIO(pdf_out)
    buffer.seek(0)
    return buffer
