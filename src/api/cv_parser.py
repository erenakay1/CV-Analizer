"""
cv_parser.py
------------
PDF, DOCX, TXT dosyalarından CV parse eder.
"""

import PyPDF2
import docx
import re
from typing import Dict
import logging

from src.core.constants import MAX_CV_CHARS

logger = logging.getLogger(__name__)


def parse_cv(file_path: str, file_type: str) -> Dict[str, str]:
    """
    CV dosyasını parse eder ve text çıkarır.
    
    Args:
        file_path: Dosya yolu
        file_type: 'pdf' | 'docx' | 'txt'
    
    Returns:
        {
            "raw_text": "Tüm CV text",
            "char_count": 1234
        }
    """
    if file_type == "pdf":
        raw_text = _parse_pdf(file_path)
    elif file_type in ["docx", "doc"]:
        raw_text = _parse_docx(file_path)
    elif file_type == "txt":
        raw_text = _parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    # Truncate if too long
    if len(raw_text) > MAX_CV_CHARS:
        logger.warning(f"CV truncated: {len(raw_text)} → {MAX_CV_CHARS} chars")
        raw_text = raw_text[:MAX_CV_CHARS] + "\n\n[... TRUNCATED]"
    
    return {
        "raw_text": raw_text.strip(),
        "char_count": len(raw_text)
    }


def _parse_pdf(file_path: str) -> str:
    """PDF'den text çıkar."""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        logger.info(f"✅ PDF parsed: {len(text)} characters")
        return text
    
    except Exception as e:
        logger.error(f"PDF parse error: {e}")
        raise ValueError(f"PDF okunamadı: {e}")


def _parse_docx(file_path: str) -> str:
    """DOCX'den text çıkar."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
        
        logger.info(f"✅ DOCX parsed: {len(text)} characters")
        return text
    
    except Exception as e:
        logger.error(f"DOCX parse error: {e}")
        raise ValueError(f"DOCX okunamadı: {e}")


def _parse_txt(file_path: str) -> str:
    """TXT dosyasını oku."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f"✅ TXT parsed: {len(text)} characters")
        return text
    
    except Exception as e:
        logger.error(f"TXT parse error: {e}")
        raise ValueError(f"TXT okunamadı: {e}")


# ─── Contact Info Extraction ─────────────────────────
def extract_contact_info(raw_text: str) -> Dict[str, str]:
    """Email, phone, LinkedIn çıkar (basit regex)."""
    contact = {
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": ""
    }
    
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text, re.IGNORECASE)
    if email_match:
        contact["email"] = email_match.group(0)
    
    # Phone (multiple formats)
    phone_patterns = [
        r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # US
        r'\+?\d{1,3}[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # International
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, raw_text)
        if phone_match:
            contact["phone"] = phone_match.group(0)
            break
    
    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/([\w-]+)', raw_text, re.IGNORECASE)
    if linkedin_match:
        contact["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
    
    # GitHub
    github_match = re.search(r'github\.com/([\w-]+)', raw_text, re.IGNORECASE)
    if github_match:
        contact["github"] = f"https://github.com/{github_match.group(1)}"
    
    return contact


# ─── Basic Section Detection (MVP) ───────────────────
def extract_sections(raw_text: str) -> Dict[str, str]:
    """
    CV'den temel section'ları çıkar (basit regex).
    Gelişmiş NLP Phase 2'de eklenecek.
    """
    sections = {
        "summary": "",
        "experience": "",
        "education": "",
        "skills": "",
        "certifications": "",
        "projects": ""
    }
    
    lines = raw_text.split('\n')
    current_section = None
    
    section_keywords = {
        'summary': ['summary', 'objective', 'profile', 'about'],
        'experience': ['experience', 'work history', 'employment', 'professional experience'],
        'education': ['education', 'academic', 'qualifications'],
        'skills': ['skills', 'technical skills', 'competencies', 'technologies'],
        'certifications': ['certification', 'licenses', 'awards'],
        'projects': ['projects', 'portfolio', 'personal projects']
    }
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Detect section headers
        for section_name, keywords in section_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                current_section = section_name
                break
        
        # Add content to current section
        if current_section and line.strip() and not any(kw in line_lower for keywords in section_keywords.values() for kw in keywords):
            sections[current_section] += line + "\n"
    
    return sections