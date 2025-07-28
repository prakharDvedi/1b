import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self):
        # Patterns for proper section headers (not fragments)
        self.section_patterns = [
            r'^[A-Z][A-Za-z\s]{15,80}$',  # Title case headers (longer than fragments)
            r'^[A-Z][A-Z\s]{8,60}$',  # ALL CAPS headers
            r'^(Comprehensive|Complete|Ultimate|General|Essential)\s+[A-Za-z\s]{10,50}$',  # Guide-style headers
            r'^(Chapter|Section|Part)\s+\d+:?\s*[A-Z][A-Za-z\s]{5,50}$',  # Structured headers
            r'^\d+(\.\d+)*\s+[A-Z][A-Za-z\s]{10,60}$',  # Numbered sections
        ]
    
    def load_pdfs(self, pdf_folder: str) -> List[Dict[str, Any]]:
        """Universal PDF loading"""
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
    
    def extract_sections(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract proper sections, not text fragments"""
        sections = []
        
        for page in document['pages']:
            page_text = page['text']
            if not page_text.strip():
                continue
            
            lines = page_text.split('\n')
            
            # Use a more structured approach to find section headers
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                if self._is_proper_section_header(line, lines, i):
                    # Extract content following this header
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
    
    def _is_proper_section_header(self, line: str, all_lines: List[str], index: int) -> bool:
        """Detect actual section headers, not fragments"""
        
        # Must be substantial length but not too long
        if len(line) < 15 or len(line) > 100:
            return False
        
        # Must not be a sentence fragment (shouldn't start with lowercase connectors)
        if line.lower().startswith(('to ', 'for ', 'with ', 'during ', 'whether ', 'and ', 'or ', 'but ')):
            return False
        
        # Must not end with incomplete words/connectors
        if line.lower().endswith((' and', ' or', ' with', ' to', ' for', ' of', ' in', ' on')):
            return False
        
        # Must start with capital letter
        if not line[0].isupper():
            return False
        
        # Check against section patterns
        for pattern in self.section_patterns:
            if re.match(pattern, line):
                return self._validate_as_header(line, all_lines, index)
        
        # Additional heuristics for proper headers
        words = line.split()
        if len(words) >= 3:
            # Check if it looks like a proper section title
            if (line.istitle() and 
                not line.endswith('.') and 
                not line.startswith('•') and
                len(line) > 20):
                return self._validate_as_header(line, all_lines, index)
            
            # Check for descriptive section headers
            important_words = ['guide', 'tips', 'adventures', 'experiences', 'highlights', 'delights']
            if (any(word.lower() in line.lower() for word in important_words) and
                len(words) <= 8 and  # Not too wordy
                line[0].isupper()):
                return self._validate_as_header(line, all_lines, index)
        
        return False
    
    def _validate_as_header(self, line: str, all_lines: List[str], index: int) -> bool:
        """Validate that this line is actually a section header by checking context"""
        
        # Check if there's substantial content following
        following_content = ""
        for i in range(index + 1, min(index + 5, len(all_lines))):
            following_content += " " + all_lines[i].strip()
        
        # Must have meaningful content following (at least 30 characters)
        if len(following_content.strip()) < 30:
            return False
        
        # The following content shouldn't be another header
        next_line = all_lines[index + 1].strip() if index + 1 < len(all_lines) else ""
        if (next_line and 
            len(next_line) > 15 and 
            (next_line.istitle() or next_line.isupper()) and
            not next_line.lower().startswith(('the ', 'this ', 'it ', 'you '))):
            return False
        
        return True
    
    def _extract_section_content(self, lines: List[str], header_index: int) -> str:
        """Extract content following a section header"""
        content_lines = []
        
        # Look for content in the next 10-15 lines
        for i in range(header_index + 1, min(header_index + 15, len(lines))):
            line = lines[i].strip()
            if not line:
                continue
            
            # Stop if we hit another section header
            if (len(line) > 15 and 
                (line.istitle() or line.isupper()) and
                not line.lower().startswith(('the ', 'this ', 'it ', 'you ', 'a ', 'an '))):
                break
            
            content_lines.append(line)
            
            # Stop when we have enough content
            if len(' '.join(content_lines)) > 200:
                break
        
        return self._clean_text(' '.join(content_lines))
    
    def _clean_text(self, text: str) -> str:
        """Clean text while preserving structure"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove bullet points but preserve content
        text = re.sub(r'^[•\-\*]\s*', '', text)
        
        return text
    
    def extract_subsections(self, top_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create high-quality subsections"""
        subsections = []
        
        for section in top_sections:
            content = section.get('content', '').strip()
            title = section['section_title']
            
            if not content:
                continue
            
            # Create comprehensive subsection content
            if len(content) > 300:
                # Find natural break point
                sentences = re.split(r'(?<=[.!?])\s+', content)
                if len(sentences) >= 2:
                    # Take first 2-3 sentences
                    selected = sentences[:3] if len(sentences) >= 3 else sentences[:2]
                    refined_text = ' '.join(selected)
                else:
                    # Fallback to character limit
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
