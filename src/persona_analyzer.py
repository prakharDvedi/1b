from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, Any, List

class PersonaAnalyzer:
    def __init__(self):
        # Load lightweight sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Enhanced persona expertise mappings
        self.persona_keywords = {
            'travel_planner': [
                'itinerary', 'accommodation', 'transportation', 'attractions', 
                'budget', 'schedule', 'booking', 'destinations', 'activities',
                'group', 'friends', 'college', 'young', 'adventure', 'nightlife',
                'planning', 'logistics', 'coordination', 'organization'
            ],
            'hr_professional': [
                'forms', 'compliance', 'onboarding', 'procedures', 'workflow', 
                'documentation', 'policies', 'training', 'employee', 'staff'
            ],
            'food_contractor': [
                'recipes', 'ingredients', 'preparation', 'serving', 'catering', 
                'dietary', 'menu', 'buffet', 'vegetarian', 'corporate', 'event'
            ],
            'researcher': [
                'methodology', 'results', 'analysis', 'literature', 'experiments', 
                'findings', 'data', 'study', 'research', 'academic'
            ],
            'student': [
                'concepts', 'examples', 'theory', 'practice', 'exercises', 
                'fundamentals', 'learning', 'study', 'education', 'tutorial'
            ],
            'analyst': [
                'trends', 'data', 'metrics', 'performance', 'comparison', 
                'insights', 'analysis', 'evaluation', 'assessment', 'review'
            ]
        }
        
        # Group travel specific keywords
        self.group_travel_keywords = [
            'group', 'friends', 'college', 'young', 'budget', 'affordable',
            'backpacking', 'hostels', 'shared', 'activities', 'nightlife',
            'adventure', 'fun', 'social', 'party', 'entertainment', 'explore'
        ]
    
    def analyze_persona(self, persona: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced persona analysis for travel planning"""
        
        # Extract persona role and job task
        persona_role = persona.get('role', '').lower()
        job_task = job.get('task', '')
        
        # Create enhanced query combining persona and specific requirements
        enhanced_query = self.create_enhanced_query(persona_role, job_task)
        
        # Generate embedding
        query_embedding = self.model.encode([enhanced_query])[0]
        
        # Extract comprehensive keywords
        keywords = self.extract_comprehensive_keywords(persona_role, job_task)
        
        # Create context object
        context = {
            'persona_role': persona_role,
            'job_task': job_task,
            'query_embedding': query_embedding,
            'keywords': keywords,
            'combined_query': enhanced_query,
            'is_group_travel': self.is_group_travel_context(job_task),
            'group_size': self.extract_group_size(job_task),
            'trip_duration': self.extract_trip_duration(job_task)
        }
        
        return context
    
    def create_enhanced_query(self, persona_role: str, job_task: str) -> str:
        """Create enhanced query string for better matching"""
        
        # Base query
        base_query = f"{persona_role}: {job_task}"
        
        # Add context based on detected patterns
        enhancements = []
        
        if 'group' in job_task.lower() or 'friends' in job_task.lower():
            enhancements.append("group travel planning")
        
        if 'college' in job_task.lower():
            enhancements.append("young travelers budget activities")
        
        if '4 days' in job_task or 'four days' in job_task:
            enhancements.append("short trip itinerary scheduling")
        
        if 'south of france' in job_task.lower():
            enhancements.append("French Riviera Mediterranean coast attractions")
        
        # Combine all elements
        if enhancements:
            enhanced_query = f"{base_query} {' '.join(enhancements)}"
        else:
            enhanced_query = base_query
        
        return enhanced_query
    
    def extract_comprehensive_keywords(self, persona_role: str, job_task: str) -> List[str]:
        """Extract comprehensive keyword list"""
        keywords = []
        
        # Add persona-specific keywords
        for persona_type, type_keywords in self.persona_keywords.items():
            if persona_type in persona_role or any(word in persona_role for word in persona_type.split('_')):
                keywords.extend(type_keywords)
        
        # Add group travel keywords if applicable
        if self.is_group_travel_context(job_task):
            keywords.extend(self.group_travel_keywords)
        
        # Extract keywords from job task
        job_words = job_task.lower().split()
        important_job_words = [
            word for word in job_words 
            if len(word) > 3 and word not in ['plan', 'trip', 'days', 'group', 'friends']
        ]
        keywords.extend(important_job_words)
        
        # Add travel planning specific keywords
        travel_keywords = [
            'accommodation', 'activities', 'attractions', 'restaurants', 
            'transportation', 'itinerary', 'schedule', 'budget', 'nightlife',
            'entertainment', 'sightseeing', 'cultural', 'cuisine', 'tips'
        ]
        keywords.extend(travel_keywords)
        
        return list(set(keywords))  # Remove duplicates
    
    def is_group_travel_context(self, job_task: str) -> bool:
        """Determine if this is group travel planning"""
        group_indicators = ['group', 'friends', 'college', 'people', 'travelers']
        return any(indicator in job_task.lower() for indicator in group_indicators)
    
    def extract_group_size(self, job_task: str) -> int:
        """Extract group size from task description"""
        import re
        
        # Look for numbers in the task
        numbers = re.findall(r'\b(\d+)\b', job_task)
        
        for num_str in numbers:
            num = int(num_str)
            if 2 <= num <= 50:  # Reasonable group size range
                return num
        
        return 1  # Default to individual travel
    
    def extract_trip_duration(self, job_task: str) -> int:
        """Extract trip duration in days"""
        import re
        
        # Look for patterns like "4 days", "four days", etc.
        day_patterns = [
            r'(\d+)\s*days?',
            r'(one|two|three|four|five|six|seven|eight|nine|ten)\s*days?'
        ]
        
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        for pattern in day_patterns:
            matches = re.findall(pattern, job_task.lower())
            for match in matches:
                if match.isdigit():
                    return int(match)
                elif match in number_words:
                    return number_words[match]
        
        return 7  # Default to 1 week
