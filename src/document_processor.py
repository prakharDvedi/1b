import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self):
        # Enhanced section patterns for Acrobat documentation
        self.section_patterns = [
            r'^[A-Z][A-Za-z\s]{15,80}$',  # Longer descriptive headers
            r'^\d+\.?\s+[A-Z][A-Za-z\s]{10,80}$',  # Numbered sections
            r'^[A-Z][A-Z\s]{10,80}$',  # ALL CAPS headers (longer)
            r'^(Create|Convert|Fill|Sign|Edit|Export|Share|Prepare|Manage)\s+[A-Za-z\s]{5,50}',  # Action-based headers
            r'^[A-Z][a-z]+\s+(forms?|PDFs?|documents?|signatures?)',  # Object-focused headers
        ]
        
        # HR-specific important keywords for section detection
        self.hr_keywords = [
            'fillable forms', 'interactive forms', 'form creation', 'prepare forms',
            'fill and sign', 'form fields', 'signatures', 'e-signatures',
            'create forms', 'manage forms', 'form distribution', 'onboarding',
            'compliance', 'workflow', 'employee', 'collect responses'
        ]
    
    def load_pdfs(self, pdf_folder: str) -> List[Dict[str, Any]]:
        """Load all PDFs from the folder"""
        documents = []
        
        for filename in os.listdir(pdf_folder):
            if filename.endswith('.pdf'):
                filepath = os.path.join(pdf_folder, filename)
                doc = fitz.open(filepath)
                
                pages = []
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    pages.append({
                        'page_number': page_num + 1,
                        'text': text,
                        'blocks': page.get_text("dict")["blocks"]
                    })
                
                documents.append({
                    'filename': filename,
                    'pages': pages,
                    'total_pages': len(doc)
                })
                
                doc.close()
        
        return documents
    
    def extract_sections(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sections with enhanced HR focus"""
        sections = []
        
        for page in document['pages']:
            page_text = page['text']
            lines = page_text.split('\n')
            
            current_section = None
            section_text = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                if self.is_hr_relevant_section_header(line, lines, i):
                    # Save previous section
                    if current_section and section_text:
                        content = self.clean_text('\n'.join(section_text))
                        if len(content) > 100:  # Higher minimum for quality
                            sections.append({
                                'document': document['filename'],
                                'page_number': page['page_number'],
                                'section_title': current_section,
                                'content': content,
                                'word_count': len(content.split())
                            })
                    
                    current_section = line
                    section_text = []
                else:
                    if current_section:
                        section_text.append(line)
            
            # Save last section on page
            if current_section and section_text:
                content = self.clean_text('\n'.join(section_text))
                if len(content) > 100:
                    sections.append({
                        'document': document['filename'],
                        'page_number': page['page_number'],
                        'section_title': current_section,
                        'content': content,
                        'word_count': len(content.split())
                    })
        
        return sections
    
    def is_hr_relevant_section_header(self, line: str, all_lines: List[str], line_index: int) -> bool:
        """Enhanced section header detection for HR relevance"""
        
        # Skip very short or fragmented headers
        if len(line) < 10 or (line.endswith('.') and not line.endswith('(Acrobat Pro)')):
            return False
        
        # Skip if it's clearly not a header (contains lots of numbers/symbols)
        if len(re.findall(r'[0-9]', line)) > len(line) * 0.3:
            return False
        
        # Check enhanced patterns
        for pattern in self.section_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # HR-specific header detection
        line_lower = line.lower()
        
        # High-priority HR keywords in headers
        hr_priority_terms = [
            'fillable', 'interactive', 'form', 'sign', 'create', 'convert',
            'fill', 'prepare', 'manage', 'distribute', 'collect', 'workflow'
        ]
        
        if any(term in line_lower for term in hr_priority_terms):
            # Additional validation for complete headers
            if (len(line) > 15 and 
                (line.istitle() or line.isupper() or 
                 any(char.isupper() for char in line)) and
                not line.endswith('.')):
                return True
        
        # Check context - next few lines should be content
        if line_index + 2 < len(all_lines):
            next_lines = ' '.join(all_lines[line_index+1:line_index+3]).strip()
            if (len(next_lines) > 50 and 
                not next_lines.isupper() and
                line.istitle()):
                return True
        
        return False
    
    def clean_text(self, raw_text: str) -> str:
        """Enhanced text cleaning for better readability"""
        if not raw_text:
            return ""
        
        # Remove bullet points and special characters
        text = raw_text.replace('•', '')
        text = text.replace('\u2022', '')
        text = text.replace('◦', '')
        
        # Fix common Unicode issues
        text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
        text = re.sub(r'\ufb00', 'ff', text)
        text = re.sub(r'\ufb01', 'fi', text)
        text = re.sub(r'\ufb02', 'fl', text)
        
        # Fix accented characters
        unicode_fixes = {
            '\u00e8': 'è', '\u00e9': 'é', '\u00ea': 'ê', '\u00eb': 'ë',
            '\u00f4': 'ô', '\u00f6': 'ö', '\u00fc': 'ü', '\u00e7': 'ç'
        }
        for old, new in unicode_fixes.items():
            text = text.replace(old, new)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '. ', text)
        
        # Clean up formatting
        text = text.replace('\n', ' ')
        text = text.strip()
        
        # Remove excessive punctuation
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\s+\.', '.', text)
        
        return text
    
    def extract_subsections(self, top_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract HR-focused subsections"""
        subsections = []
        
        for section in top_sections:
            content = section['content']
            
            # Split into sentences for better subsection creation
            sentences = re.split(r'(?<=[.!?])\s+', content)
            
            # Group sentences into meaningful subsections
            current_subsection = ""
            sentence_count = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Add sentence to current subsection
                if current_subsection:
                    current_subsection += " " + sentence
                else:
                    current_subsection = sentence
                
                sentence_count += 1
                
                # Create subsection when we have good content
                if ((sentence_count >= 2 and len(current_subsection) > 150) or 
                    len(current_subsection) > 400):
                    
                    # Ensure proper ending
                    if not current_subsection.endswith(('.', '!', '?')):
                        current_subsection += '.'
                    
                    # Only include if it's HR-relevant
                    if self.is_hr_relevant_content(current_subsection):
                        subsections.append({
                            'document': section['document'],
                            'page_number': section['page_number'],
                            'refined_text': current_subsection.strip(),
                            'source_section': section['section_title']
                        })
                    
                    current_subsection = ""
                    sentence_count = 0
            
            # Add remaining content if substantial and relevant
            if current_subsection and len(current_subsection) > 100:
                if not current_subsection.endswith(('.', '!', '?')):
                    current_subsection += '.'
                
                if self.is_hr_relevant_content(current_subsection):
                    subsections.append({
                        'document': section['document'],
                        'page_number': section['page_number'],
                        'refined_text': current_subsection.strip(),
                        'source_section': section['section_title']
                    })
        
        return subsections
    
    def is_hr_relevant_content(self, content: str) -> bool:
        """Check if content is relevant for HR professional"""
        content_lower = content.lower()
        
        # Must contain at least one HR-relevant term
        hr_relevant_terms = [
            'form', 'field', 'fill', 'sign', 'create', 'interactive',
            'fillable', 'document', 'pdf', 'acrobat', 'employee',
            'workflow', 'process', 'manage', 'distribute'
        ]
        
        relevant_count = sum(1 for term in hr_relevant_terms if term in content_lower)
        
        # Should not contain too many irrelevant terms
        irrelevant_terms = [
            'generative ai', 'artificial intelligence', 'machine learning',
            'visio', 'postscript', 'color management', 'prepress'
        ]
        
        irrelevant_count = sum(1 for term in irrelevant_terms if term in content_lower)
        
        return relevant_count >= 2 and irrelevant_count == 0
