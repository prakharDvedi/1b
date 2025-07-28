import re
from typing import Dict, Any, List

class PersonaAnalyzer:
    def __init__(self):
        # No predefined mappings - everything is dynamic
        pass
    
    def analyze_persona(self, persona: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze persona dynamically without any domain assumptions"""
        
        persona_role = persona.get('role', '').strip()
        job_task = job.get('task', '').strip()
        
        # Extract keywords purely from input text - no predefined lists
        persona_keywords = self._extract_keywords_generic(persona_role)
        job_keywords = self._extract_keywords_generic(job_task)
        
        # Dynamically extract ANY action words from the text
        action_words = self._extract_dynamic_actions(job_task)
        
        # Combine all keywords
        all_keywords = list(set(persona_keywords + job_keywords + action_words))
        
        context = {
            'persona_role': persona_role.lower(),
            'job_task': job_task.lower(),
            'keywords': all_keywords,
            'combined_query': f"{persona_role} {job_task}".lower(),
            'query_length': len(f"{persona_role} {job_task}".split())
        }
        
        return context
    
    def _extract_keywords_generic(self, text: str) -> List[str]:
        """Extract meaningful keywords from any text without domain bias"""
        if not text:
            return []
        
        # Universal stop words only
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may',
            'might', 'must', 'a', 'an', 'this', 'that', 'these', 'those', 'from'
        }
        
        # Extract all words 3+ characters long
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        meaningful_words = [word for word in words if word not in stop_words]
        
        return list(set(meaningful_words))
    
    def _extract_dynamic_actions(self, text: str) -> List[str]:
        """Dynamically extract action words without predefined lists"""
        if not text:
            return []
        
        # Look for verbs in common sentence patterns - completely generic
        action_patterns = [
            r'\b(\w+)\s+(?:a|an|the|some|many|all)\s+\w+',  # "verb + article + noun"
            r'\b(\w+)\s+\w+(?:ing|ed|er|ly)\b',             # "verb + word with suffix"
            r'\b(\w+)\s+(?:and|or)\s+\w+',                  # "verb + conjunction + word"
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, text.lower())
            actions.extend(matches)
        
        # Filter to keep only likely action words (verbs)
        # This is still generic - based on word structure, not domain
        verb_endings = ['ate', 'ize', 'ify', 'ise']  # Common verb suffixes
        filtered_actions = []
        
        for word in actions:
            if (len(word) > 3 and 
                (any(word.endswith(ending) for ending in verb_endings) or
                 word.endswith('e') or word.endswith('y'))):
                filtered_actions.append(word)
        
        return list(set(filtered_actions))
