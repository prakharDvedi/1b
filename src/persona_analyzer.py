from typing import Dict, Any, List
import re

class PersonaAnalyzer:
    def __init__(self):
        # Enhanced persona expertise mappings for HR professional
        self.persona_keywords = {
            'hr_professional': [
                # Core HR form keywords
                'fillable forms', 'form creation', 'interactive forms', 'form fields',
                'fill and sign', 'prepare forms', 'form wizard', 'form templates',
                
                # Onboarding and compliance
                'onboarding', 'compliance', 'employee documentation', 'workflow',
                'approval process', 'digital signatures', 'e-signatures',
                
                # Document management
                'document management', 'form distribution', 'collect responses',
                'track submissions', 'form validation', 'required fields',
                
                # HR processes
                'employee forms', 'hiring documents', 'policy forms',
                'training records', 'performance reviews', 'benefits enrollment'
            ],
            'travel_planner': [
                'itinerary', 'accommodation', 'transportation', 'attractions',
                'budget', 'schedule', 'booking', 'destinations', 'activities'
            ],
            'food_contractor': [
                'recipes', 'ingredients', 'preparation', 'serving', 'catering',
                'dietary', 'menu', 'buffet', 'vegetarian', 'corporate', 'event'
            ]
        }
    
    def analyze_persona(self, persona: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze persona without ML dependencies"""
        
        persona_role = persona.get('role', '').lower()
        job_task = job.get('task', '')
        
        # Create enhanced query
        enhanced_query = self.create_enhanced_query(persona_role, job_task)
        
        # Extract comprehensive keywords
        keywords = self.extract_comprehensive_keywords(persona_role, job_task)
        
        # Create context object (without embeddings)
        context = {
            'persona_role': persona_role,
            'job_task': job_task,
            'query_embedding': None,  # No ML model needed
            'keywords': keywords,
            'combined_query': enhanced_query,
            'is_hr_context': self.is_hr_context(persona_role, job_task),
            'specific_needs': self.extract_specific_needs(job_task)
        }
        
        return context
    
    def create_enhanced_query(self, persona_role: str, job_task: str) -> str:
        """Create enhanced query for HR professional"""
        base_query = f"{persona_role}: {job_task}"
        
        enhancements = []
        
        if 'hr' in persona_role.lower() or 'human resources' in persona_role.lower():
            enhancements.append("form creation fillable interactive")
        
        if 'fillable forms' in job_task.lower():
            enhancements.append("prepare forms fill sign interactive fields")
        
        if 'onboarding' in job_task.lower():
            enhancements.append("employee documents workflow signatures")
        
        if 'compliance' in job_task.lower():
            enhancements.append("required fields validation tracking")
        
        if enhancements:
            enhanced_query = f"{base_query} {' '.join(enhancements)}"
        else:
            enhanced_query = base_query
        
        return enhanced_query
    
    def extract_comprehensive_keywords(self, persona_role: str, job_task: str) -> List[str]:
        """Extract comprehensive keyword list for HR professional"""
        keywords = []
        
        # Add persona-specific keywords
        for persona_type, type_keywords in self.persona_keywords.items():
            if persona_type in persona_role.replace(' ', '_').lower():
                keywords.extend(type_keywords)
        
        # Add HR-specific keywords if HR persona
        if 'hr' in persona_role.lower() or 'human resources' in persona_role.lower():
            hr_specific = [
                'forms', 'fillable', 'interactive', 'fields', 'signatures',
                'workflow', 'compliance', 'onboarding', 'employee', 'create',
                'manage', 'distribute', 'collect', 'track', 'validate'
            ]
            keywords.extend(hr_specific)
        
        # Extract keywords from job task
        job_words = job_task.lower().split()
        important_job_words = [
            word for word in job_words 
            if len(word) > 3 and word not in ['create', 'manage', 'forms']
        ]
        keywords.extend(important_job_words)
        
        return list(set(keywords))  # Remove duplicates
    
    def is_hr_context(self, persona_role: str, job_task: str) -> bool:
        """Determine if this is HR context"""
        hr_indicators = [
            'hr', 'human resources', 'onboarding', 'compliance', 
            'employee', 'forms', 'fillable'
        ]
        combined_text = f"{persona_role} {job_task}".lower()
        return any(indicator in combined_text for indicator in hr_indicators)
    
    def extract_specific_needs(self, job_task: str) -> List[str]:
        """Extract specific needs from job task"""
        needs = []
        
        if 'create' in job_task.lower():
            needs.append('form_creation')
        if 'manage' in job_task.lower():
            needs.append('form_management')
        if 'fillable' in job_task.lower():
            needs.append('interactive_forms')
        if 'onboarding' in job_task.lower():
            needs.append('onboarding_workflow')
        if 'compliance' in job_task.lower():
            needs.append('compliance_tracking')
        
        return needs
