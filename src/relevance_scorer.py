import numpy as np
from typing import List, Dict, Any

class RelevanceScorer:
    def __init__(self):
        # No sentence transformer needed for minimal version
        pass
    
    def score_sections(self, sections: List[Dict[str, Any]], 
                      persona_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score and rank sections with document diversity"""
        
        scored_sections = []
        
        for section in sections:
            # Calculate relevance score
            score = self.calculate_relevance_score(section, persona_context)
            
            section_with_score = section.copy()
            section_with_score['relevance_score'] = score
            scored_sections.append(section_with_score)
        
        # Sort by relevance score (descending)
        scored_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Ensure document diversity in top results
        balanced_sections = self.ensure_document_diversity(scored_sections)
        
        # Add importance rank
        for i, section in enumerate(balanced_sections):
            section['importance_rank'] = i + 1
        
        return balanced_sections
    
    def ensure_document_diversity(self, ranked_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure representation from multiple documents"""
        doc_counts = {}
        balanced_sections = []
        remaining_sections = []
        
        # First pass: Take top sections from each document (max 2 per doc initially)
        for section in ranked_sections:
            doc = section['document']
            if doc_counts.get(doc, 0) < 2:
                balanced_sections.append(section)
                doc_counts[doc] = doc_counts.get(doc, 0) + 1
            else:
                remaining_sections.append(section)
        
        # Second pass: Fill remaining slots with best remaining sections
        for section in remaining_sections:
            if len(balanced_sections) >= 15:  # Limit total sections
                break
            balanced_sections.append(section)
        
        return balanced_sections
    
    def calculate_relevance_score(self, section: Dict[str, Any], 
                                 persona_context: Dict[str, Any]) -> float:
        """Calculate relevance score using keyword matching (no ML)"""
        
        # Combine section title and content for analysis
        section_text = f"{section['section_title']} {section['content']}".lower()
        
        # 1. Keyword overlap score
        keyword_score = self.calculate_keyword_overlap(
            section_text, persona_context['keywords']
        )
        
        # 2. Structural importance score
        structural_score = self.calculate_structural_importance(section)
        
        # 3. Length score (optimal range)
        length_score = self.calculate_length_score(section)
        
        # 4. Travel planning specific score
        travel_score = self.calculate_travel_planning_score(section, persona_context)
        
        # Weighted combination (no semantic similarity since no ML models)
        final_score = (
            0.4 * keyword_score +
            0.3 * structural_score +
            0.15 * length_score +
            0.15 * travel_score
        )
        
        return final_score
    
    def calculate_keyword_overlap(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword overlap score"""
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        
        return matches / len(keywords)
    
    def calculate_structural_importance(self, section: Dict[str, Any]) -> float:
        """Calculate structural importance with travel focus"""
        title = section['section_title'].lower()
        
        # Higher scores for travel-relevant section types
        important_terms = {
            'guide': 0.95, 'overview': 0.9, 'introduction': 0.85,
            'cities': 0.9, 'destinations': 0.9, 'places': 0.8,
            'activities': 0.9, 'things to do': 0.95, 'attractions': 0.9,
            'adventures': 0.85, 'experiences': 0.85,
            'accommodation': 0.9, 'hotels': 0.85, 'restaurants': 0.8,
            'dining': 0.75, 'cuisine': 0.8, 'culinary': 0.8,
            'nightlife': 0.85, 'entertainment': 0.8, 'bars': 0.7,
            'tips': 0.9, 'tricks': 0.85, 'advice': 0.8,
            'planning': 0.95, 'itinerary': 0.9, 'schedule': 0.8,
            'packing': 0.7, 'preparation': 0.7, 'transportation': 0.8,
            'cultural': 0.75, 'history': 0.6, 'traditions': 0.7,
            'comprehensive': 0.8, 'complete': 0.7, 'essential': 0.8
        }
        
        max_score = 0.5  # Default score
        for term, score in important_terms.items():
            if term in title:
                max_score = max(max_score, score)
        
        return max_score
    
    def calculate_length_score(self, section: Dict[str, Any]) -> float:
        """Calculate score based on optimal section length"""
        word_count = section.get('word_count', 0)
        
        # Optimal range: 100-800 words for travel planning
        if 100 <= word_count <= 800:
            return 1.0
        elif word_count < 100:
            return max(0.3, word_count / 100)
        else:  # > 800 words
            return max(0.4, 800 / word_count)
    
    def calculate_travel_planning_score(self, section: Dict[str, Any], 
                                      persona_context: Dict[str, Any]) -> float:
        """Score based on travel planning relevance"""
        content = f"{section['section_title']} {section['content']}".lower()
        
        # Travel planning specific terms
        planning_terms = {
            'group': 0.9, 'friends': 0.8, 'college': 0.7, 'budget': 0.8,
            'accommodation': 0.9, 'hotel': 0.7, 'hostel': 0.8, 'booking': 0.6,
            'itinerary': 0.9, 'plan': 0.7, 'schedule': 0.6, 'day': 0.5,
            'transportation': 0.8, 'train': 0.6, 'bus': 0.6, 'flight': 0.6,
            'activities': 0.8, 'attractions': 0.7, 'sightseeing': 0.7,
            'restaurant': 0.7, 'dining': 0.6, 'food': 0.6, 'cuisine': 0.7,
            'nightlife': 0.8, 'entertainment': 0.7, 'party': 0.6,
            'tips': 0.8, 'advice': 0.7, 'guide': 0.8, 'overview': 0.7,
            'cities': 0.8, 'destinations': 0.7, 'places': 0.6,
            'packing': 0.6, 'preparation': 0.5, 'travel': 0.6
        }
        
        score = 0.0
        total_weight = 0.0
        
        for term, weight in planning_terms.items():
            if term in content:
                score += weight
                total_weight += weight
        
        # Normalize by total possible weight
        if total_weight > 0:
            return min(1.0, score / 5.0)  # Cap at 1.0
        
        return 0.0
