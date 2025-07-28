#!/usr/bin/env python3
"""
Main entry point for Challenge 1B: Persona-Driven Document Intelligence
"""

import json
import os
import sys
import time
from pathlib import Path
from src.document_processor import DocumentProcessor
from src.persona_analyzer import PersonaAnalyzer
from src.relevance_scorer import RelevanceScorer
from src.output_formatter import OutputFormatter

class DocumentIntelligenceSystem:
    def __init__(self):
        print("Initializing Document Intelligence System...")
        self.doc_processor = DocumentProcessor()
        self.persona_analyzer = PersonaAnalyzer()
        self.relevance_scorer = RelevanceScorer()
        self.output_formatter = OutputFormatter()
        print("System initialized successfully!")
    
    def process_collection(self, collection_path):
        """Process a single document collection with enhanced logic"""
        print(f"Processing collection: {collection_path}")
        start_time = time.time()
        
        try:
            # Load input configuration
            input_file = os.path.join(collection_path, "challenge1b_input.json")
            if not os.path.exists(input_file):
                print(f"Error: Input file {input_file} not found")
                return None
            
            with open(input_file, 'r') as f:
                input_config = json.load(f)
            
            print(f"Loaded configuration for persona: {input_config['persona']['role']}")
            
            # Load and process PDFs
            pdf_folder = os.path.join(collection_path, "PDFs")
            if not os.path.exists(pdf_folder):
                print(f"Error: PDF folder {pdf_folder} not found")
                return None
            
            print(f"Loading PDFs from {pdf_folder}...")
            documents = self.doc_processor.load_pdfs(pdf_folder)
            print(f"Loaded {len(documents)} documents")
            
            # Extract sections from all documents
            print("Extracting sections from documents...")
            all_sections = []
            for doc in documents:
                sections = self.doc_processor.extract_sections(doc)
                all_sections.extend(sections)
                print(f"  - {doc['filename']}: {len(sections)} sections")
            
            print(f"Total sections extracted: {len(all_sections)}")
            
            # Analyze persona and job requirements
            print("Analyzing persona and job requirements...")
            persona_context = self.persona_analyzer.analyze_persona(
                input_config["persona"], 
                input_config["job_to_be_done"]
            )
            
            # Score and rank sections
            print("Scoring and ranking sections...")
            ranked_sections = self.relevance_scorer.score_sections(
                all_sections, persona_context
            )
            
            print(f"Top 5 sections:")
            for i, section in enumerate(ranked_sections[:5]):
                print(f"  {i+1}. {section['section_title'][:50]}... (Score: {section['relevance_score']:.3f})")
            
            # Extract top subsections
            print("Extracting subsections...")
            subsections = self.doc_processor.extract_subsections(
                ranked_sections[:10]  # Top 10 sections
            )
            
            print(f"Generated {len(subsections)} subsections")
            
            # Format output
            print("Formatting output...")
            output_data = self.output_formatter.format_output(
                input_config, ranked_sections, subsections, start_time
            )
            
            # Save results
            output_file = os.path.join(collection_path, "challenge1b_output.json")
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            processing_time = time.time() - start_time
            print(f"Collection processed successfully in {processing_time:.2f} seconds")
            print(f"Output saved to: {output_file}")
            
            return output_data
            
        except Exception as e:
            print(f"Error processing collection: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <collection_path>")
        print("\nExample:")
        print("  python main.py \"Collection 1\"")
        print("  python main.py \"Collection 2\"")
        print("  python main.py \"Collection 3\"")
        sys.exit(1)
    
    collection_path = sys.argv[1]
    
    # Initialize and run the system
    system = DocumentIntelligenceSystem()
    result = system.process_collection(collection_path)
    
    if result is None:
        print("Processing failed!")
        sys.exit(1)
    else:
        print("Processing completed successfully!")

if __name__ == "__main__":
    main()
