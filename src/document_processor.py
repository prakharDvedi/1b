import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Any

# … existing imports …
BULLET_RE = re.compile(r'^[•◦\-–o]\s+', re.UNICODE)   # bullets & “o ”

class DocumentProcessor:
    # keep your __init__ & load_pdfs unchanged …

    # ------------ REPLACE is_section_header WITH THIS -----------------
    def is_generic_section_header(self, line:str, all_lines:list, idx:int) -> bool:
        """Reject cooking steps & accept only real headers."""
        # bullets / recipe steps → reject
        if BULLET_RE.match(line.lower()):
            return False
        if line.startswith('o '):                  # leading “o ”
            return False
        # too short / ends with comma etc.
        if len(line) < 8 or line[-1] in ',:;':
            return False

        # must start with capital letter
        if not line[0].isupper():                 
            return False

        # must contain at least 2 words with capitalisation
        words = line.split()
        cap_words = sum(1 for w in words if w[0].isupper())
        if cap_words < 2:
            return False

        # next two lines should look like body text ( > 25 chars )
        nxt = ' '.join(all_lines[idx+1: idx+3])
        if len(nxt) < 25:
            return False

        return True

    
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
        """Universal section extraction without domain bias"""
        sections = []
        
        for page in document['pages']:
            page_text = page['text']
            if not page_text.strip():
                continue
            
            lines = page_text.split('\n')
            
            current_section = None
            section_text = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                if self._is_universal_section_header(line, lines, i):
                    # Save previous section
                    if current_section and section_text:
                        content = self._clean_text(' '.join(section_text))
                        if self._is_valid_section(current_section, content):
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
                content = self._clean_text(' '.join(section_text))
                if self._is_valid_section(current_section, content):
                    sections.append({
                        'document': document['filename'],
                        'page_number': page['page_number'],
                        'section_title': current_section,
                        'content': content,
                        'word_count': len(content.split())
                    })
        
        return sections
    
    def _is_universal_section_header(self, line: str, all_lines: List[str], line_index: int) -> bool:
        """Universal section header detection"""
        
        # Basic validation
        if len(line) < 5 or len(line) > 120:
            return False
        
        # Skip obvious non-headers
        if (line.endswith(',') or line.endswith(';') or 
            line.startswith('•') or line.startswith('-') or line.startswith('*') or
            line.lower().startswith(('and ', 'or ', 'but ', 'the ', 'a ', 'an '))):
            return False
        
        # Check universal patterns
        for pattern in self.universal_patterns:
            if re.match(pattern, line):
                return self._validate_header_context(line, all_lines, line_index)
        
        # Additional heuristic checks
        words = line.split()
        if len(words) >= 2:
            # Check if it looks like a proper header
            if (line.istitle() and not line.endswith('.') and 
                len(line) > 10 and len(line) < 80):
                return self._validate_header_context(line, all_lines, line_index)
            
            # Check for descriptive headers
            if (any(word[0].isupper() for word in words) and 
                len([w for w in words if len(w) > 3]) >= 2 and
                not any(char.isdigit() for char in line[:10])):  # Not starting with numbers
                return self._validate_header_context(line, all_lines, line_index)
        
        return False
    
    def _validate_header_context(self, line: str, all_lines: List[str], line_index: int) -> bool:
        """Validate header by checking surrounding context"""
        
        # Check following lines contain substantial content
        following_content = ""
        for i in range(line_index + 1, min(line_index + 4, len(all_lines))):
            following_content += " " + all_lines[i].strip()
        
        # Must have substantial following content
        if len(following_content.strip()) < 30:
            return False
        
        # Following content shouldn't be another header
        next_line = all_lines[line_index + 1].strip() if line_index + 1 < len(all_lines) else ""
        if next_line and (next_line.isupper() or next_line.istitle()) and len(next_line) < 50:
            return False
        
        return True
    
    def _is_valid_section(self, title: str, content: str) -> bool:
        """Validate section quality universally"""
        
        # Minimum content requirements
        if not content or len(content.strip()) < 20:
            return False
        
        # Title quality checks
        if not title or len(title.strip()) < 5:
            return False
        
        # Avoid sections that are just lists of single words
        content_words = content.split()
        if len(content_words) < 10:
            return False
        
        # Check content-title relationship
        title_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', title.lower()))
        content_words_set = set(re.findall(r'\b[a-zA-Z]{3,}\b', content.lower()))
        
        # Some overlap between title and content is expected
        if title_words and content_words_set:
            overlap = len(title_words.intersection(content_words_set))
            if overlap == 0 and len(title_words) > 2:
                return False
        
        return True
    
    def _clean_text(self, text: str) -> str:
        """Universal text cleaning"""
        if not text:
            return ""
        
        # Remove bullet points and special formatting
        text = re.sub(r'[•\-\*]\s*', '', text)
        
        # Fix Unicode issues
        unicode_fixes = {
            '\ufb00': 'ff', '\ufb01': 'fi', '\ufb02': 'fl',
            '\u00e8': 'è', '\u00e9': 'é', '\u00ea': 'ê',
            '\u00f4': 'ô', '\u00f6': 'ö', '\u00fc': 'ü',
            '\u2019': "'", '\u201c': '"', '\u201d': '"'
        }
        
        for old, new in unicode_fixes.items():
            text = text.replace(old, new)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', ' ', text)
        
        return text.strip()
    
    def extract_subsections(self, top_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Universal subsection extraction"""
        subsections = []
        
        for section in top_sections:
            content = section.get('content', '').strip()
            title = section['section_title']
            
            if not content:
                continue
            
            # Create meaningful subsections
            refined_text = self._create_universal_subsection(title, content)
            
            if refined_text and len(refined_text) > 30:
                subsections.append({
                    'document': section['document'],
                    'page_number': section['page_number'],
                    'refined_text': refined_text,
                    'source_section': title
                })
        
        return subsections
    
    def _create_universal_subsection(self, title: str, content: str) -> str:
        """Create subsection using universal approach"""
        
        # Strategy 1: If content is concise, use title + content
        if len(content) <= 300:
            return f"{title}: {content}"
        
        # Strategy 2: Extract first meaningful sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        if len(sentences) >= 2:
            # Take first 2-3 sentences that form a coherent unit
            selected_sentences = []
            char_count = 0
            
            for sentence in sentences[:5]:  # Look at first 5 sentences
                sentence = sentence.strip()
                if len(sentence) > 10:  # Meaningful sentence
                    selected_sentences.append(sentence)
                    char_count += len(sentence)
                    
                    if len(selected_sentences) >= 2 and char_count > 150:
                        break
                    if char_count > 400:
                        break
            
            if selected_sentences:
                return f"{title}: {' '.join(selected_sentences)}"
        
        # Strategy 3: Take first logical paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            first_para = paragraphs[0]
            if len(first_para) > 50:
                truncated = first_para[:400] if len(first_para) > 400 else first_para
                return f"{title}: {truncated}"
        
        # Strategy 4: Fallback - truncate content intelligently
        truncated = content[:300] if len(content) > 300 else content
        # Try to end at a natural break
        if len(content) > 300:
            last_period = truncated.rfind('.')
            last_space = truncated.rfind(' ')
            
            if last_period > 200:
                truncated = truncated[:last_period + 1]
            elif last_space > 250:
                truncated = truncated[:last_space] + "..."
        
        return f"{title}: {truncated}"
