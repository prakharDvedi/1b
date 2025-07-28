import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self):
        # Improved section patterns for better detection
        self.section_patterns = [
            r'^[A-Z][A-Za-z\s]{10,80}$',  # Title case headers (minimum 10 chars)
            r'^\d+\.?\s+[A-Z][A-Za-z\s]{5,80}$',  # Numbered sections
            r'^[A-Z][A-Z\s]{5,80}$',  # ALL CAPS headers (minimum 5 chars)
            r'^Chapter\s+\d+:?\s+[A-Za-z\s]{3,50}$',  # Chapter headers
            r'^Section\s+\d+:?\s+[A-Za-z\s]{3,50}$',  # Section headers
        ]
        
        # Keywords that indicate important sections for travel planning
        self.important_keywords = [
            'guide', 'overview', 'introduction', 'cities', 'attractions', 
            'activities', 'accommodation', 'restaurants', 'hotels', 'tips',
            'planning', 'itinerary', 'transportation', 'nightlife', 'cuisine',
            'experiences', 'adventures', 'entertainment', 'cultural', 'packing'
        ]
    
    def load_pdfs(self, pdf_folder: str) -> List[Dict[str, Any]]:
        """Load all PDFs from the folder"""
        documents = []
        
        for filename in os.listdir(pdf_folder):
            if filename.endswith('.pdf'):
                filepath = os.path.join(pdf_folder, filename)
                doc = fitz.open(filepath)
                
                # Extract text with page information
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
        """Extract sections from a document with improved detection"""
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
                
                # Check if line is a section header
                if self.is_section_header(line, lines, i):
                    # Save previous section
                    if current_section and section_text:
                        content = self.clean_text('\n'.join(section_text))
                        if len(content) > 50:  # Minimum content length
                            sections.append({
                                'document': document['filename'],
                                'page_number': page['page_number'],
                                'section_title': current_section,
                                'content': content,
                                'word_count': len(content.split())
                            })
                    
                    # Start new section
                    current_section = line
                    section_text = []
                else:
                    if current_section:
                        section_text.append(line)
            
            # Save last section on page
            if current_section and section_text:
                content = self.clean_text('\n'.join(section_text))
                if len(content) > 50:
                    sections.append({
                        'document': document['filename'],
                        'page_number': page['page_number'],
                        'section_title': current_section,
                        'content': content,
                        'word_count': len(content.split())
                    })
        
        return sections
    
    def is_section_header(self, line: str, all_lines: List[str], line_index: int) -> bool:
        """Improved section header detection"""
        # Basic length and format checks
        if len(line) < 5 or len(line) > 100:
            return False
        
        # Skip if it's just a fragment or ends with incomplete text
        if line.endswith(':') and len(line) < 15:
            return False
        
        # Check against improved patterns
        for pattern in self.section_patterns:
            if re.match(pattern, line):
                return True
        
        # Additional heuristics
        
        # Check if it's a proper title (title case or all caps)
        words = line.split()
        if len(words) >= 2:
            # Title case check
            if all(word[0].isupper() for word in words if word.isalpha()):
                return True
            
            # All caps check (but not too long)
            if line.isupper() and len(line) < 60:
                return True
        
        # Check for important travel-related keywords
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in self.important_keywords):
            # Additional validation - should look like a title
            if (line.istitle() or line.isupper()) and not line.endswith('.'):
                return True
        
        # Check formatting context (if next line is content-like)
        if line_index + 1 < len(all_lines):
            next_line = all_lines[line_index + 1].strip()
            if next_line and len(next_line) > 20 and not next_line.isupper():
                # Current line might be a header if it's short and title-like
                if len(line) < 50 and (line.istitle() or line.isupper()):
                    return True
        
        return False
    
    def clean_text(self, raw_text: str) -> str:
        """Clean text by removing formatting artifacts"""
        if not raw_text:
            return ""
        
        # Remove bullet points and special characters
        text = raw_text.replace('•', '')
        text = text.replace('\u2022', '')  # Another bullet point format
        
        # Remove Unicode artifacts
        text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
        text = re.sub(r'\ufb00', 'ff', text)  # Fix ligature
        text = re.sub(r'\u00e8', 'è', text)   # Fix accented characters
        text = re.sub(r'\u00e9', 'é', text)
        text = re.sub(r'\u00f4', 'ô', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Clean up formatting
        text = text.replace('\n', ' ')
        text = text.strip()
        
        return text
    
    def extract_subsections(self, top_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relevant subsections with better text processing"""
        subsections = []
        
        for section in top_sections:
            content = section['content']
            
            # Split content into meaningful paragraphs
            paragraphs = re.split(r'\.\s+', content)
            
            # Process paragraphs into coherent subsections
            current_subsection = ""
            sentence_count = 0
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # Add sentence to current subsection
                if current_subsection:
                    current_subsection += ". " + para
                else:
                    current_subsection = para
                
                sentence_count += 1
                
                # Create subsection when we have 2-4 sentences or reach good length
                if (sentence_count >= 2 and len(current_subsection) > 100) or len(current_subsection) > 300:
                    # Ensure it ends properly
                    if not current_subsection.endswith('.'):
                        current_subsection += '.'
                    
                    subsections.append({
                        'document': section['document'],
                        'page_number': section['page_number'],
                        'refined_text': current_subsection.strip(),
                        'source_section': section['section_title']
                    })
                    
                    current_subsection = ""
                    sentence_count = 0
            
            # Add remaining content if substantial
            if current_subsection and len(current_subsection) > 50:
                if not current_subsection.endswith('.'):
                    current_subsection += '.'
                
                subsections.append({
                    'document': section['document'],
                    'page_number': section['page_number'],
                    'refined_text': current_subsection.strip(),
                    'source_section': section['section_title']
                })
        
        return subsections
