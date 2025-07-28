import json
from datetime import datetime
from typing import Dict, Any, List

class OutputFormatter:
    def format_output(self, input_config: Dict[str, Any], 
                     ranked_sections: List[Dict[str, Any]],
                     subsections: List[Dict[str, Any]], 
                     start_time: float) -> Dict[str, Any]:
        """Universal output formatting"""
        
        # Extract document filenames universally
        input_documents = []
        if 'documents' in input_config and input_config['documents']:
            input_documents = [doc.get('filename', doc.get('title', '')) 
                             for doc in input_config['documents']]
        else:
            # Fallback: extract from sections
            input_documents = list(set(section['document'] for section in ranked_sections))
            input_documents.sort()  # Consistent ordering
        
        # Format metadata
        metadata = {
            "input_documents": input_documents,
            "persona": input_config['persona'].get('role', 'Unknown'),
            "job_to_be_done": input_config['job_to_be_done'].get('task', 'Unknown'),
            "processing_timestamp": datetime.now().isoformat() + "Z"
        }
        
        # Format extracted sections (limit to top 15)
        extracted_sections = []
        for section in ranked_sections[:15]:
            extracted_sections.append({
                "document": section['document'],
                "section_title": section['section_title'],
                "importance_rank": section['importance_rank'],
                "page_number": section['page_number']
            })
        
        # Format subsection analysis (limit for readability)
        subsection_analysis = []
        for subsection in subsections[:10]:  # Limit to top 10
            subsection_analysis.append({
                "document": subsection['document'],
                "refined_text": subsection['refined_text'][:500],  # Reasonable length
                "page_number": subsection['page_number']
            })
        
        return {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
