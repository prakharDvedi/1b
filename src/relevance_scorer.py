import numpy as np
from typing import List, Dict, Any
import re

class RelevanceScorer:
    def __init__(self):
        pass
    
    def score_sections(self, sections: List[Dict[str, Any]], 
                      persona_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Completely generic scoring without domain assumptions"""
        
        scored_sections = []
        
        for section in sections:
            score = self.calculate_generic_relevance_score(section, persona_context)
            
            section_with_score = section.copy()
            section_with_score['relevance_score'] = score
            scored_sections.append(section_with_score)
        
        # Sort by relevance score (descending)
        scored_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Generic document diversity
        balanced_sections = self.ensure_generic_diversity(scored_sections)
        
        # Add importance rank
        for i, section in enumerate(balanced_sections):
            section['importance_rank'] = i + 1
        
        return balanced_sections
    
    def calculate_generic_relevance_score(self, section: Dict[str, Any], 
                                        persona_context: Dict[str, Any]) -> float:
        """Generic scoring based only on input context"""
        
        section_text = f"{section['section_title']} {section['content']}".lower()
        
        # 1. Dynamic keyword matching (most important)
        keyword_score = self.calculate_dynamic_keyword_match(
            section_text, persona_context
        )
        
        # 2. Action relevance (based on verbs in job task)
        action_score = self.calculate_action_relevance(
            section_text, persona_context['job_task']
        )
        
        # 3. Section quality (generic heuristics)
        quality_score = self.calculate_generic_section_quality(section)
        
        # 4. Context coherence (how well section matches overall context)
        coherence_score = self.calculate_context_coherence(
            section_text, persona_context
        )
        
        # Equal weights - no domain bias
        final_score = (
            0.4 * keyword_score +
            0.25 * action_score +
            0.2 * quality_score +
            0.15 * coherence_score
        )
        
        return final_score
    
    def calculate_dynamic_keyword_match(self, section_text: str, 
                                      persona_context: Dict[str, Any]) -> float:
        """Dynamic keyword matching without predefined lists"""
        
        # Extract keywords from persona and job dynamically
        persona_words = self.extract_meaningful_words(persona_context['persona_role'])
        job_words = self.extract_meaningful_words(persona_context['job_task'])
        
        all_keywords = persona_words + job_words
        
        if not all_keywords:
            return 0.0
        
        # Calculate matches with different weights
        exact_matches = sum(1 for keyword in all_keywords if keyword in section_text)
        partial_matches = sum(1 for keyword in all_keywords 
                            if any(keyword in word for word in section_text.split()))
        
        # Weighted score
        match_score = (exact_matches * 2 + partial_matches) / (len(all_keywords) * 2)
        
        return min(1.0, match_score)
    
    def extract_meaningful_words(self, text: str) -> List[str]:
        """Extract meaningful words from any text"""
        
        # Common stop words to exclude
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 
            'could', 'can', 'may', 'might', 'must', 'a', 'an', 'this', 
            'that', 'these', 'those', 'from', 'up', 'down', 'out', 'off', 
            'over', 'under', 'again', 'further', 'then', 'once'
        }
        
        # Extract words, filter by length and stop words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        meaningful_words = [word for word in words 
                          if word not in stop_words and len(word) > 2]
        
        return list(set(meaningful_words))  # Remove duplicates
    
    def calculate_action_relevance(self, section_text: str, job_task: str) -> float:
        """Score based on action words in job task"""
        
        # Extract action verbs from job task
        action_words = re.findall(r'\b(create|make|build|manage|handle|organize|'
                                r'develop|design|implement|execute|process|'
                                r'analyze|review|evaluate|assess|plan|prepare|'
                                r'distribute|collect|track|monitor|control|'
                                r'maintain|update|modify|edit|convert|export|'
                                r'import|share|send|receive|sign|fill|complete)\b', 
                                job_task.lower())
        
        if not action_words:
            return 0.5  # Neutral score if no clear actions
        
        # Check how many action words appear in section
        action_matches = sum(1 for action in action_words if action in section_text)
        
        return min(1.0, action_matches / len(action_words))
    
    def calculate_generic_section_quality(self, section: Dict[str, Any]) -> float:
        """Generic section quality without domain assumptions"""
        
        title = section['section_title']
        content = section.get('content', '')
        
        quality_score = 0.0
        
        # Title quality checks
        if len(title) >= 15 and len(title) <= 80:  # Good length
            quality_score += 0.3
        
        if title[0].isupper() and not title.endswith('.'):  # Proper header format
            quality_score += 0.2
        
        if len(title.split()) >= 3:  # Multi-word titles are usually better
            quality_score += 0.2
        
        # Content quality checks
        word_count = len(content.split())
        if 50 <= word_count <= 500:  # Good content length
            quality_score += 0.3
        elif word_count > 0:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def calculate_context_coherence(self, section_text: str, 
                                  persona_context: Dict[str, Any]) -> float:
        """How well the section fits the overall context"""
        
        # Combine persona and job into context
        full_context = f"{persona_context['persona_role']} {persona_context['job_task']}".lower()
        context_words = set(self.extract_meaningful_words(full_context))
        section_words = set(self.extract_meaningful_words(section_text))
        
        if not context_words or not section_words:
            return 0.5
        
        # Calculate word overlap
        overlap = len(context_words.intersection(section_words))
        union = len(context_words.union(section_words))
        
        # Jaccard similarity
        if union == 0:
            return 0.5
        
        return overlap / union
    
    def ensure_generic_diversity(self, ranked_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generic document diversity without favorites"""
        
        balanced_sections = []
        doc_counts = {}
        total_docs = len(set(section['document'] for section in ranked_sections))
        
        # Dynamic limit based on number of documents
        max_per_doc = max(1, 15 // total_docs) if total_docs > 0 else 3
        
        for section in ranked_sections:
            doc = section['document']
            if doc_counts.get(doc, 0) < max_per_doc:
                balanced_sections.append(section)
                doc_counts[doc] = doc_counts.get(doc, 0) + 1
            
            if len(balanced_sections) >= 15:
                break
        
        # If we don't have enough sections, add more from high-scoring sections
        if len(balanced_sections) < 5:
            for section in ranked_sections:
                if section not in balanced_sections:
                    balanced_sections.append(section)
                if len(balanced_sections) >= 5:
                    break
        
        return balanced_sections
