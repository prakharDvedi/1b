import fitz
import re
import os
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self):
        self.section_patterns = [
            r'^[A-Z][A-Za-z\s]{15,80}$',
            r'^[A-Z][A-Z\s]{8,60}$',
            r'^(Comprehensive|Complete|Ultimate|General|Essential)\s+[A-Za-z\s]{10,50}$',
            r'^(Chapter|Section|Part)\s+\d+:?\s*[A-Z][A-Za-z\s]{5,50}$',
            r'^\d+(\.\d+)*\s+[A-Z][A-Za-z\s]{10,60}$',
        ]
    
    # Load PDF documents from specified folder
    def load_pdfs(self, pdf_folder: str) -> List[Dict[str, Any]]:
        documents = []
        
        if not os.path.exists(pdf_folder):
            return documents
        
        for filename in os.listdir(pdf_folder):
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(pdf_folder, filename)
                try:
                    doc = fitz.open(filepath)
                    
                    pages = []
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        text = page.get_text()
                        pages.append({
                            'page_number': page_num + 1,
                            'text': text
                        })
                    
                    documents.append({
                        'filename': filename,
                        'pages': pages,
                        'total_pages': len(doc)
                    })
                    
                    doc.close()
                    
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    continue
        
        return documents
    
    # Extract sections from document pages
    def extract_sections(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        sections = []
        
        for page in document['pages']:
            page_text = page['text']
            if not page_text.strip():
                continue
            
            lines = page_text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                if self._is_proper_section_header(line, lines, i):
                    content = self._extract_section_content(lines, i)
                    
                    if content and len(content) > 50:
                        sections.append({
                            'document': document['filename'],
                            'page_number': page['page_number'],
                            'section_title': line,
                            'content': content,
                            'word_count': len(content.split())
                        })
        
        return sections
    
    # Check if line is a proper section header
    def _is_proper_section_header(self, line: str, all_lines: List[str], index: int) -> bool:
        if len(line) < 15 or len(line) > 100:
            return False
        
        if line.lower().startswith(('to ', 'for ', 'with ', 'during ', 'whether ', 'and ', 'or ', 'but ')):
            return False
        
        if line.lower().endswith((' and', ' or', ' with', ' to', ' for', ' of', ' in', ' on')):
            return False
        
        if not line[0].isupper():
            return False
        
        for pattern in self.section_patterns:
            if re.match(pattern, line):
                return self._validate_as_header(line, all_lines, index)
        
        words = line.split()
        if len(words) >= 3:
            if (line.istitle() and 
                not line.endswith('.') and 
                not line.startswith('•') and
                len(line) > 20):
                return self._validate_as_header(line, all_lines, index)
            
            important_words = ['guide', 'tips', 'adventures', 'experiences', 'highlights', 'delights']
            if (any(word.lower() in line.lower() for word in important_words) and
                len(words) <= 8 and
                line[0].isupper()):
                return self._validate_as_header(line, all_lines, index)
        
        return False
    
    # Validate line as section header by checking context
    def _validate_as_header(self, line: str, all_lines: List[str], index: int) -> bool:
        following_content = ""
        for i in range(index + 1, min(index + 5, len(all_lines))):
            following_content += " " + all_lines[i].strip()
        
        if len(following_content.strip()) < 30:
            return False
        
        next_line = all_lines[index + 1].strip() if index + 1 < len(all_lines) else ""
        if (next_line and 
            len(next_line) > 15 and 
            (next_line.istitle() or next_line.isupper()) and
            not next_line.lower().startswith(('the ', 'this ', 'it ', 'you '))):
            return False
        
        return True
    
    # Extract content following a section header
    def _extract_section_content(self, lines: List[str], header_index: int) -> str:
        content_lines = []
        
        for i in range(header_index + 1, min(header_index + 15, len(lines))):
            line = lines[i].strip()
            if not line:
                continue
            
            if (len(line) > 15 and 
                (line.istitle() or line.isupper()) and
                not line.lower().startswith(('the ', 'this ', 'it ', 'you ', 'a ', 'an '))):
                break
            
            content_lines.append(line)
            
            if len(' '.join(content_lines)) > 200:
                break
        
        return self._clean_text(' '.join(content_lines))
    
    # Clean text while preserving structure
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        text = re.sub(r'^[•\-\*]\s*', '', text)
        
        return text
    
    # Create high-quality subsections from top sections
    def extract_subsections(self, top_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        subsections = []
        
        for section in top_sections:
            content = section.get('content', '').strip()
            title = section['section_title']
            
            if not content:
                continue
            
            if len(content) > 300:
                sentences = re.split(r'(?<=[.!?])\s+', content)
                if len(sentences) >= 2:
                    selected = sentences[:3] if len(sentences) >= 3 else sentences[:2]
                    refined_text = ' '.join(selected)
                else:
                    refined_text = content[:300]
                    last_space = refined_text.rfind(' ')
                    if last_space > 250:
                        refined_text = refined_text[:last_space]
            else:
                refined_text = content
            
            subsections.append({
                'document': section['document'],
                'page_number': section['page_number'],
                'refined_text': refined_text,
                'source_section': title
            })
        
        return subsections
