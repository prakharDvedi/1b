import numpy as np
from typing import List, Dict, Any
import re
import math

class RelevanceScorer:
    def __init__(self):
        # No domain-specific initialization
        pass
    
    def score_sections(self, sections: List[Dict[str, Any]], 
                      persona_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score sections using pure algorithmic approach"""
        
        if not sections:
            return []
        
        scored_sections = []
        
        for section in sections:
            score = self._calculate_universal_relevance_score(section, persona_context)
            
            section_with_score = section.copy()
            section_with_score['relevance_score'] = score
            scored_sections.append(section_with_score)
        
        # Sort by relevance score
        scored_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Apply universal diversity
        balanced_sections = self._ensure_universal_diversity(scored_sections)
        
        # Add importance rank
        for i, section in enumerate(balanced_sections):
            section['importance_rank'] = i + 1
        
        return balanced_sections
    
    def _calculate_universal_relevance_score(self, section: Dict[str, Any], 
                                           persona_context: Dict[str, Any]) -> float:
        """Universal relevance scoring without domain bias"""
        
        section_text = f"{section['section_title']} {section.get('content', '')}".lower()
        query_text = persona_context['combined_query']
        keywords = persona_context['keywords']
        
        # 1. Keyword Frequency Score
        keyword_score = self._calculate_keyword_frequency(section_text, keywords)
        
        # 2. Text Similarity Score (using simple word overlap)
        similarity_score = self._calculate_text_similarity(section_text, query_text)
        
        # 3. Section Quality Score (universal heuristics)
        quality_score = self._calculate_section_quality(section)
        
        # 4. Content Completeness Score
        completeness_score = self._calculate_content_completeness(section)
        
        # 5. Title Relevance Score
        title_relevance = self._calculate_title_relevance(section['section_title'], keywords)
        
        # Universal weighted combination
        final_score = (
            0.30 * keyword_score +
            0.25 * similarity_score +
            0.20 * quality_score +
            0.15 * completeness_score +
            0.10 * title_relevance
        )
        
        return final_score
    
    def _calculate_keyword_frequency(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword frequency using TF-IDF-like approach"""
        if not keywords or not text:
            return 0.0
        
        text_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
        keyword_set = set(keyword.lower() for keyword in keywords)
        
        # Direct matches
        direct_matches = len(text_words.intersection(keyword_set))
        
        # Partial matches (substring)
        partial_matches = 0
        for keyword in keyword_set:
            if any(keyword in word for word in text_words):
                partial_matches += 1
        
        # Calculate frequency score
        total_possible = len(keyword_set)
        frequency_score = (direct_matches * 2 + partial_matches) / (total_possible * 2)
        
        return min(1.0, frequency_score)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using Jaccard coefficient"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower()))
        words2 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_section_quality(self, section: Dict[str, Any]) -> float:
        """Universal section quality metrics"""
        title = section.get('section_title', '')
        content = section.get('content', '')
        
        quality_score = 0.0
        
        # Title quality
        if title:
            title_length = len(title)
            if 10 <= title_length <= 80:  # Optimal title length
                quality_score += 0.3
            elif 5 <= title_length <= 120:  # Acceptable range
                quality_score += 0.1
            
            # Title structure (starts with capital, not all caps unless short)
            if title[0].isupper() and not (title.isupper() and len(title) > 20):
                quality_score += 0.2
        
        # Content quality
        if content:
            word_count = len(content.split())
            if 50 <= word_count <= 500:  # Optimal content length
                quality_score += 0.3
            elif 20 <= word_count <= 800:  # Acceptable range
                quality_score += 0.2
            elif word_count > 0:
                quality_score += 0.1
        
        # Avoid generic titles
        generic_indicators = ['introduction', 'conclusion', 'overview', 'summary', 'preface', 'appendix']
        if not any(generic.lower() in title.lower() for generic in generic_indicators):
            quality_score += 0.2
        
        return min(1.0, quality_score)
    
    def _calculate_content_completeness(self, section: Dict[str, Any]) -> float:
        """Measure content completeness using universal indicators"""
        content = section.get('content', '').lower()
        title = section.get('section_title', '').lower()
        
        if not content:
            return 0.0
        
        completeness_score = 0.0
        
        # Check for structured content indicators
        structure_indicators = [
            r'\d+\.',  # Numbered lists
            r'[•\-\*]',  # Bullet points
            r':',  # Colons (definitions, explanations)
            r';',  # Semicolons (detailed lists)
        ]
        
        for pattern in structure_indicators:
            if re.search(pattern, content):
                completeness_score += 0.15
        
        # Check for explanatory content
        explanation_words = ['how', 'what', 'why', 'when', 'where', 'which', 'because', 'since', 'therefore']
        explanation_count = sum(1 for word in explanation_words if word in content)
        completeness_score += min(0.3, explanation_count * 0.05)
        
        # Content-title alignment
        title_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', title))
        content_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', content))
        
        if title_words and content_words:
            alignment = len(title_words.intersection(content_words)) / len(title_words)
            completeness_score += alignment * 0.25
        
        return min(1.0, completeness_score)
    
    def _calculate_title_relevance(self, title: str, keywords: List[str]) -> float:
        """Calculate how relevant the title is to the keywords"""
        if not title or not keywords:
            return 0.0
        
        title_lower = title.lower()
        title_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', title_lower))
        keyword_set = set(keyword.lower() for keyword in keywords)
        
        if not title_words:
            return 0.0
        
        # Direct word matches in title
        matches = len(title_words.intersection(keyword_set))
        
        # Partial matches
        partial_matches = sum(1 for keyword in keyword_set 
                            if any(keyword in word for word in title_words))
        
        relevance = (matches * 2 + partial_matches) / (len(keyword_set) * 2)
        return min(1.0, relevance)
    
    def _ensure_universal_diversity(self, ranked_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure document diversity without domain-specific preferences"""
        if not ranked_sections:
            return []
        
        # Calculate optimal distribution
        unique_docs = list(set(section['document'] for section in ranked_sections))
        total_sections_needed = min(15, len(ranked_sections))
        sections_per_doc = max(1, total_sections_needed // len(unique_docs))
        
        balanced_sections = []
        doc_counts = {}
        
        # First pass: distribute evenly across documents
        for section in ranked_sections:
            doc = section['document']
            if doc_counts.get(doc, 0) < sections_per_doc:
                balanced_sections.append(section)
                doc_counts[doc] = doc_counts.get(doc, 0) + 1
        
        # Second pass: fill remaining slots with highest scoring sections
        remaining_slots = total_sections_needed - len(balanced_sections)
        for section in ranked_sections:
            if len(balanced_sections) >= total_sections_needed:
                break
            if section not in balanced_sections:
                balanced_sections.append(section)
        
        return balanced_sections[:total_sections_needed]
