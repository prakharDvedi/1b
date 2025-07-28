# Approach Explanation: Persona-Driven Document Intelligence

## Methodology Overview

Our solution implements a multi-stage pipeline that processes PDF documents and extracts relevant content based on specific personas and their job requirements. The system is designed to be generic, handling diverse document types, personas, and tasks while maintaining strict performance constraints.

## Core Components

### 1. Document Processing Pipeline
We use PyMuPDF for robust PDF text extraction with precise page number tracking. Our section detection algorithm combines pattern matching with heuristic analysis to identify document structure. The system recognizes various header formats including numbered sections, capitalized titles, and markdown-style formatting.

### 2. Persona-Task Understanding
The system employs the lightweight `all-MiniLM-L6-v2` sentence transformer (90MB) to create semantic embeddings of persona roles and job requirements. We maintain a knowledge base of persona-specific keywords that enhance relevance scoring for different professional contexts.

### 3. Multi-Factor Relevance Scoring
Our scoring engine combines four key factors:
- **Semantic Similarity (50%)**: Cosine similarity between section content and persona-job embeddings
- **Keyword Overlap (30%)**: Frequency of persona-specific terms in section text  
- **Structural Importance (15%)**: Weight based on section type (methodology, results, etc.)
- **Length Optimization (5%)**: Preference for sections in the optimal 50-500 word range

### 4. Hierarchical Content Extraction
The system first ranks all document sections, then extracts granular subsections from the top-ranked content. This two-level approach ensures both broad topic coverage and detailed information extraction.

## Performance Optimizations

To meet the strict constraints (CPU-only, <1GB models, <60s processing), we implement several optimizations:
- Quantized sentence transformers for fast inference
- Batch processing of document sections
- Efficient text chunking for subsection analysis
- Cached embeddings to avoid recomputation

## Generalization Strategy

The system handles diverse domains through:
- Domain-agnostic section detection patterns
- Flexible persona keyword mapping
- Adaptive scoring weights based on content characteristics
- Scalable processing pipeline supporting 3-15 documents per collection

This approach ensures robust performance across the challenge's varied test cases while maintaining high relevance accuracy for persona-specific content extraction.
