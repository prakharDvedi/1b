import re
from typing import Dict, Any, List

class PersonaAnalyzer:
    def __init__(self):
        # No predefined domain mappings - everything is dynamic
        pass
    
    def analyze_persona(self, persona: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze persona dynamically without any domain assumptions"""
        
        persona_role = persona.get('role', '').strip()
        job_task = job.get('task', '').strip()
        
        # Extract keywords purely from input text
        persona_keywords = self._extract_keywords(persona_role)
        job_keywords = self._extract_keywords(job_task)
        action_words = self._extract_action_words(job_task)
        
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
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from any text"""
        if not text:
            return []
        
        # Universal stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may',
            'might', 'must', 'a', 'an', 'this', 'that', 'these', 'those', 'from',
            'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then'
        }
        
        # Extract words 3+ characters long
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        meaningful_words = [word for word in words if word not in stop_words]
        
        return list(set(meaningful_words))
    
    def _extract_action_words(self, text: str) -> List[str]:
        """Extract action verbs from text using universal patterns"""
        if not text:
            return []
        
        # Universal action verb pattern
        action_pattern = r'\b(create|make|build|develop|design|manage|handle|organize|' \
                        r'analyze|review|evaluate|assess|plan|prepare|implement|execute|' \
                        r'process|generate|produce|deliver|provide|support|maintain|' \
                        r'coordinate|facilitate|optimize|improve|enhance|update|modify|' \
                        r'edit|convert|transform|compile|collect|gather|distribute|' \
                        r'present|communicate|collaborate|lead|direct|supervise)\b'
        
        return re.findall(action_pattern, text.lower())
