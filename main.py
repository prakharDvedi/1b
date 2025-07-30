#!/usr/bin/env python3

import json
import os
import sys
import time
import argparse
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
    
    def process_documents(self, config_file=None, pdf_folder=None, persona_role=None,
                         job_task=None, output_file=None):
        print("Starting document processing...")
        start_time = time.time()
        
        try:
            if config_file and os.path.exists(config_file):
                print(f"Loading configuration from: {config_file}")
                with open(config_file, 'r') as f:
                    input_config = json.load(f)
                
                persona_role = input_config.get('persona', {}).get('role', persona_role)
                job_task = input_config.get('job_to_be_done', {}).get('task', job_task)
                
                if not pdf_folder:
                    config_dir = os.path.dirname(config_file)
                    potential_pdf_folder = os.path.join(config_dir, "PDFs")
                    if os.path.exists(potential_pdf_folder):
                        pdf_folder = potential_pdf_folder
                    else:
                        pdf_folder = config_dir
            else:
                input_config = {
                    'persona': {'role': persona_role or 'General User'},
                    'job_to_be_done': {'task': job_task or 'Analyze documents'},
                    'documents': []
                }
            
            if not pdf_folder or not os.path.exists(pdf_folder):
                print(f"Error: PDF folder '{pdf_folder}' not found or not specified")
                return None
            
            if not persona_role:
                print("Error: Persona role not specified")
                return None
            
            if not job_task:
                print("Error: Job task not specified")
                return None
            
            print(f"Configuration:")
            print(f"  - Persona: {persona_role}")
            print(f"  - Task: {job_task}")
            print(f"  - PDF Folder: {pdf_folder}")
            
            print(f"Loading PDFs from {pdf_folder}...")
            documents = self.doc_processor.load_pdfs(pdf_folder)
            
            if not documents:
                print("Error: No PDF documents found")
                return None
            
            print(f"Loaded {len(documents)} documents")
            
            print("Extracting sections from documents...")
            all_sections = []
            for doc in documents:
                sections = self.doc_processor.extract_sections(doc)
                all_sections.extend(sections)
                print(f"  - {doc['filename']}: {len(sections)} sections")
            
            print(f"Total sections extracted: {len(all_sections)}")
            
            if not all_sections:
                print("Warning: No sections extracted from documents")
                return None
            
            print("Analyzing persona and job requirements...")
            persona_context = self.persona_analyzer.analyze_persona(
                input_config["persona"],
                input_config["job_to_be_done"]
            )
            
            print("Scoring and ranking sections...")
            ranked_sections = self.relevance_scorer.score_sections(
                all_sections, persona_context
            )
            
            print(f"Top 5 sections:")
            for i, section in enumerate(ranked_sections[:5]):
                print(f"  {i+1}. {section['section_title'][:50]}... (Score: {section['relevance_score']:.3f})")
            
            print("Extracting subsections...")
            subsections = self.doc_processor.extract_subsections(
                ranked_sections[:10]
            )
            
            print(f"Generated {len(subsections)} subsections")
            
            print("Formatting output...")
            output_data = self.output_formatter.format_output(
                input_config, ranked_sections, subsections, start_time
            )
            
            if not output_file:
                outputs_dir = "Outputs"
                if not os.path.exists(outputs_dir):
                    os.makedirs(outputs_dir)
                
                collection_name = "analysis"
                import re
                
                if config_file:
                    config_dir = os.path.dirname(config_file)
                    config_folder = os.path.basename(config_dir)
                    if 'collection' in config_folder.lower():
                        match = re.search(r'collection\s*(\d+)', config_folder.lower())
                        if match:
                            collection_name = f"collection_{match.group(1)}"
                elif pdf_folder:
                    folder_name = os.path.basename(pdf_folder.rstrip('/\\'))
                    if 'collection' in folder_name.lower():
                        match = re.search(r'collection\s*(\d+)', folder_name.lower())
                        if match:
                            collection_name = f"collection_{match.group(1)}"
                    else:
                        parent_folder = os.path.basename(os.path.dirname(pdf_folder))
                        if 'collection' in parent_folder.lower():
                            match = re.search(r'collection\s*(\d+)', parent_folder.lower())
                            if match:
                                collection_name = f"collection_{match.group(1)}"
                
                output_file = os.path.join(outputs_dir, f"{collection_name}_output.json")
            else:
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            processing_time = time.time() - start_time
            print(f"Processing completed successfully in {processing_time:.2f} seconds")
            print(f"Output saved to: {output_file}")
            
            return output_data
            
        except Exception as e:
            print(f"Error during processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def main():
    parser = argparse.ArgumentParser(
        description="Document Intelligence System - Analyze PDF documents based on persona and task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --config "Collection 1/challenge1b_input.json"
  python main.py --pdf-folder "my_pdfs" --persona "Data Analyst" --task "Extract key insights"
  python main.py --pdf-folder "docs" --persona "Manager" --task "Summarize reports" --output "results.json"
  python main.py "Collection 1"
        """
    )
    
    parser.add_argument('collection_path', nargs='?',
                       help='Legacy: Path to collection folder (for backward compatibility)')
    parser.add_argument('--config', '-c',
                       help='Path to JSON configuration file')
    parser.add_argument('--pdf-folder', '-p',
                       help='Path to folder containing PDF files')
    parser.add_argument('--persona', '-r',
                       help='Persona role (e.g., "Data Analyst", "Manager")')
    parser.add_argument('--task', '-t',
                       help='Task description (e.g., "Analyze quarterly reports")')
    parser.add_argument('--output', '-o',
                       help='Output file path (default: auto-generated in Outputs folder)')
    
    args = parser.parse_args()
    
    system = DocumentIntelligenceSystem()
    
    if args.collection_path:
        print("Running in legacy collection mode...")
        
        input_file = os.path.join(args.collection_path, "challenge1b_input.json")
        pdf_folder = os.path.join(args.collection_path, "PDFs")
        
        if os.path.exists(input_file):
            result = system.process_documents(
                config_file=input_file,
                pdf_folder=pdf_folder if os.path.exists(pdf_folder) else args.collection_path,
                output_file=args.output
            )
        else:
            result = system.process_documents(
                pdf_folder=args.collection_path,
                persona_role=args.persona or "General User",
                job_task=args.task or "Analyze documents",
                output_file=args.output
            )
    
    elif args.config or args.pdf_folder:
        result = system.process_documents(
            config_file=args.config,
            pdf_folder=args.pdf_folder,
            persona_role=args.persona,
            job_task=args.task,
            output_file=args.output
        )
    
    else:
        parser.print_help()
        sys.exit(1)
    
    if result is None:
        print("Processing failed!")
        sys.exit(1)
    else:
        print("Processing completed successfully!")

if __name__ == "__main__":
    main()
