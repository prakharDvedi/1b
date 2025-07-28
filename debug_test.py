import os
import sys
import json

def test_basic_setup():
    collection_path = "Collection 1"
    
    print("=== DEBUG TEST ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Collection path exists: {os.path.exists(collection_path)}")
    
    # Test input file
    input_file = os.path.join(collection_path, "challenge1b_input.json")
    print(f"Input file exists: {os.path.exists(input_file)}")
    
    if os.path.exists(input_file):
        try:
            with open(input_file, 'r') as f:
                config = json.load(f)
            print(f"Input file loaded successfully")
            print(f"Persona: {config.get('persona', {}).get('role', 'Unknown')}")
        except Exception as e:
            print(f"Error loading input file: {e}")
    
    # Test PDFs folder
    pdf_folder = os.path.join(collection_path, "PDFs")
    print(f"PDFs folder exists: {os.path.exists(pdf_folder)}")
    
    if os.path.exists(pdf_folder):
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        print(f"Found {len(pdf_files)} PDF files:")
        for pdf in pdf_files[:3]:  # Show first 3
            print(f"  - {pdf}")
    
    # Test imports
    print("\n=== TESTING IMPORTS ===")
    try:
        import sentence_transformers
        print("✓ sentence_transformers imported")
    except ImportError as e:
        print(f"✗ sentence_transformers failed: {e}")
    
    try:
        import fitz  # PyMuPDF
        print("✓ PyMuPDF imported")
    except ImportError as e:
        print(f"✗ PyMuPDF failed: {e}")
    
    try:
        from src.document_processor import DocumentProcessor
        print("✓ DocumentProcessor imported")
    except ImportError as e:
        print(f"✗ DocumentProcessor failed: {e}")
        print("Make sure you have the src/ folder with all the Python files")

if __name__ == "__main__":
    test_basic_setup()
