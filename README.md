# Document Intelligence System - Generalized Version

A fast, CPU-only document analysis tool that intelligently extracts relevant sections from PDF documents based on persona-driven goals. Now fully generalized to work with any PDF documents and use cases.

## 🌐 Usage

### Modern Usage (Recommended)

#### Using Configuration File
```bash
# Use a configuration file
python main.py --config examples/business_analysis_config.json --pdf-folder "my_documents"

# Or specify PDF folder in config and just use config
python main.py --config my_config.json
```

#### Direct Command Line
```bash
# Analyze PDFs with inline persona and task
python main.py --pdf-folder "documents" --persona "Data Analyst" --task "Extract key insights from reports"

# With custom output file
python main.py --pdf-folder "pdfs" --persona "Manager" --task "Summarize quarterly results" --output "analysis.json"

# Single PDF file
python main.py --pdf-folder "report.pdf" --persona "Researcher" --task "Extract methodology"
```

### Legacy Usage (Backward Compatibility)
```bash
# Still works with existing collection structure
python main.py "Collection 1"
python main.py "Collection 2"
```

### Docker Usage
```bash
# Build the container
docker build -t document-intelligence .

# Run with modern syntax
docker run --rm -v "${PWD}:/app" document-intelligence python main.py --pdf-folder "documents" --persona "Analyst" --task "Extract insights"

# Run with legacy syntax
docker run --rm -v "${PWD}:/app" document-intelligence python main.py "Collection 1"
```

---

## 📋 Configuration System

### Configuration File Template

Use [`config_template.json`](config_template.json) as a starting point:

```json
{
  "persona": {
    "role": "Your Role Here",
    "description": "Optional: Detailed description of the persona"
  },
  "job_to_be_done": {
    "task": "Your task description here",
    "context": "Optional: Additional context about the task",
    "requirements": "Optional: Specific requirements or constraints"
  },
  "processing_options": {
    "min_content_length": 50,
    "max_sections": 15,
    "max_subsections": 10,
    "recursive_search": false
  },
  "output_options": {
    "include_statistics": true,
    "max_text_length": 500,
    "include_scores": true
  }
}
```

### Example Configurations

- [`examples/business_analysis_config.json`](examples/business_analysis_config.json) - For business document analysis
- [`examples/research_config.json`](examples/research_config.json) - For academic research papers

---

## 📊 Enhanced Output Format

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "document_count": 2,
    "persona": "Data Analyst",
    "job_to_be_done": "Extract key insights",
    "processing_timestamp": "2025-01-30T11:00:00.000Z",
    "processing_time_seconds": 2.45,
    "system_version": "2.0.0-generic"
  },
  "statistics": {
    "total_sections_found": 45,
    "sections_included": 15,
    "subsections_included": 10,
    "total_words_analyzed": 12500,
    "average_relevance_score": 0.742,
    "max_relevance_score": 0.956,
    "min_relevance_score": 0.234,
    "sections_per_document": {
      "doc1.pdf": 8,
      "doc2.pdf": 7
    }
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "section_title": "Key Performance Indicators",
      "importance_rank": 1,
      "page_number": 3,
      "word_count": 156,
      "relevance_score": 0.956,
      "extraction_method": "line_analysis"
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "Detailed analysis text...",
      "page_number": 3,
      "source_section": "Key Performance Indicators",
      "text_length": 245
    }
  ]
}
```

---

## 🌟 Key Features

* ✅ **Fully Generalized**: Works with any PDF documents and use cases
* ✅ **Flexible Input**: Support for config files, command line args, or legacy collections
* ✅ **CPU-only**: No GPU or CUDA dependencies
* ✅ **Multiple PDF Sources**: Single files, folders, or recursive directory search
* ✅ **Enhanced Section Detection**: Multiple extraction methods for better coverage
* ✅ **Configurable Processing**: Customizable limits and options
* ✅ **Rich Statistics**: Detailed analysis metrics and performance data
* ✅ **Backward Compatible**: Still works with existing collection structure

---

## 🔧 Command Line Options

```
python main.py --help

positional arguments:
  collection_path       Legacy: Path to collection folder (for backward compatibility)

optional arguments:
  -h, --help           show this help message and exit
  --config, -c         Path to JSON configuration file
  --pdf-folder, -p     Path to folder containing PDF files
  --persona, -r        Persona role (e.g., "Data Analyst", "Manager")
  --task, -t           Task description (e.g., "Analyze quarterly reports")
  --output, -o         Output file path (default: auto-generated in Outputs folder)
```

---

## 🎯 Use Cases & Examples

### Business Analysis
```bash
python main.py --pdf-folder "quarterly_reports" \
               --persona "Business Analyst" \
               --task "Extract KPIs and growth metrics for executive summary"
```

### Academic Research
```bash
python main.py --config examples/research_config.json \
               --pdf-folder "research_papers" \
               --output "literature_review.json"
```

### Legal Document Review
```bash
python main.py --pdf-folder "contracts" \
               --persona "Legal Counsel" \
               --task "Identify key terms and potential risks"
```

### Technical Documentation
```bash
python main.py --pdf-folder "manuals" \
               --persona "Technical Writer" \
               --task "Extract installation and configuration procedures"
```

---

## 🔹 Advanced Features

### Recursive Directory Search
```bash
python main.py --pdf-folder "documents" --persona "Analyst" --task "Analyze all reports" --recursive
```

### Custom Processing Options
Create a config file with custom settings:
```json
{
  "processing_options": {
    "min_content_length": 100,
    "max_sections": 25,
    "recursive_search": true
  }
}
```

### Multiple Extraction Methods
The system now uses multiple approaches:
- **Line Analysis**: Traditional line-by-line section detection
- **Paragraph Analysis**: For documents with different formatting
- **Pattern Matching**: Generic patterns that work across domains

---

## 🛠️ Installation & Setup

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
```txt
PyMuPDF==1.23.0
numpy==1.24.3
```

### Docker Setup
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["python", "main.py", "--help"]
```

---

## 🚧 Migration from Legacy Version

### Old Usage
```bash
python main.py "Collection 1"
```

### New Equivalent
```bash
# If you have the collection structure
python main.py "Collection 1"  # Still works!

# Or modernize it
python main.py --config "Collection 1/challenge1b_input.json" --pdf-folder "Collection 1/PDFs"

# Or go fully generic
python main.py --pdf-folder "Collection 1/PDFs" --persona "Travel Planner" --task "Plan a trip"
```

---

## 🎓 Algorithm Details

The system uses a sophisticated multi-stage approach:

### 1. **Document Loading**
- Supports single files, folders, and recursive search
- Automatic text cleaning and validation
- Metadata extraction and statistics

### 2. **Section Extraction**
- Multiple extraction methods for better coverage
- Generic patterns that work across domains
- Duplicate detection and quality filtering

### 3. **Relevance Scoring**
- **Keyword Overlap (40%)**: Direct and partial matches
- **Text Similarity (30%)**: Jaccard similarity
- **Quality Score (20%)**: Length, structure, formatting
- **Content Richness (10%)**: Vocabulary diversity

### 4. **Output Generation**
- Configurable limits and formatting
- Rich statistics and metadata
- Multiple output formats supported

---

## 🚀 Success Metrics

| Feature | Status |
|---------|--------|
| Fully Generalized | ✅ |
| Backward Compatible | ✅ |
| CPU-only | ✅ |
| < 1GB Footprint | ✅ |
| Dockerized | ✅ |
| Flexible Configuration | ✅ |
| Enhanced Analytics | ✅ |

---

## 🎓 License

Created for Adobe India Hackathon 2025 — Challenge 1B.
**Now fully generalized for any document analysis use case.**
