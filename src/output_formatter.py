import json
from datetime import datetime
from typing import Dict, Any, List

class OutputFormatter:
    def format_output(self, input_config: Dict[str, Any], 
                     ranked_sections: List[Dict[str, Any]],
                     subsections: List[Dict[str, Any]], 
                     start_time: float) -> Dict[str, Any]:
        """Format the final output according to challenge requirements"""
        
        # Extract document filenames
        input_documents = [doc['filename'] for doc in input_config.get('documents', [])]
        if not input_documents:  # Fallback to section documents
            input_documents = list(set(section['document'] for section in ranked_sections))
        
        # Format metadata
        metadata = {
            "input_documents": input_documents,
            "persona": input_config['persona']['role'],
            "job_to_be_done": input_config['job_to_be_done']['task'],
            "processing_timestamp": datetime.now().isoformat() + "Z"
        }
        
        # Format extracted sections (top 15)
        extracted_sections = []
        for section in ranked_sections[:15]:
            extracted_sections.append({
                "document": section['document'],
                "page_number": section['page_number'],
                "section_title": section['section_title'],
                "importance_rank": section['importance_rank']
            })
        
        # Format subsection analysis
        subsection_analysis = []
        for subsection in subsections:
            subsection_analysis.append({
                "document": subsection['document'],
                "refined_text": subsection['refined_text'][:500],  # Limit length
                "page_number": subsection['page_number']
            })
        
        return {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
