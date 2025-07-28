# Challenge 1B: Persona-Driven Document Intelligence System

A fast, CPU-only document analysis tool that intelligently extracts relevant sections from large PDF collections based on persona-driven goals.

## 🌐 Usage

### CLI

```bash
python main.py "Collection 1"
```

### Docker

```bash
docker build -t 1b-minimal .
docker run --rm -v "${PWD}:/app" 1b-minimal python main.py "Collection 2"
```

---

## 📊 Output Format

```json
{
  "metadata": {
    "input_documents": [...],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "..."
  },
  "extracted_sections": [...],
  "subsection_analysis": [...]
}
```

---

---

## 🌟 Overview

This system processes diverse PDF documents and extracts the most relevant sections based on a defined persona and their job-to-be-done. It avoids heavy ML models, using keyword-based relevance scoring and quality heuristics to deliver fast and accurate results.

---

## 🔹 Key Features

* ✅ **CPU-only**: No GPU or CUDA dependencies
* ✅ **Compact**: Under 50MB total size
* ✅ **Modular scoring**: Relevance driven by persona-task match
* ✅ **Flexible**: Works across domains like HR, Travel, Food
* ✅ **Dockerized**: Fully portable and reproducible

---

## 🎓 Relevance Scoring Algorithm

### 1. **Keyword Overlap (40%)**

```python
keywords = extract_keywords(persona + job_task)
direct = count_exact_matches(text, keywords)
partial = count_substring_matches(text, keywords)
score = (direct * 2 + partial) / (total_keywords * 2)
```

### 2. **Text Similarity (30%)**

```python
sim = jaccard(set(query_words), set(section_words))
```

### 3. **Quality Score (20%)**

* Title: 15–80 chars
* Body: 50–500 words
* Proper case
* No intro/conclusion fluff

### 4. **Content Richness (10%)**

```python
richness = len(set(words)) / len(words)
```

---

## 📊 Document Diversity Handling

Ensures no single PDF dominates:

```python
unique_docs = count_unique_documents(sections)
limit = max(1, 15 // unique_docs)
```

---

## 📄 Sample Use Cases

### 1. Travel Planner

* **Task**: Plan 4-day trip for 10 friends
* **Output**: Best regions, activities, logistics

### 2. HR Professional

* **Task**: Build and manage onboarding forms
* **Output**: Fill & sign workflows, compliance automation

### 3. Food Contractor

* **Task**: Curate vegetarian buffet
* **Output**: Vegetarian recipes, buffet strategy, allergens

---

## 🔧 Dependencies

```txt
PyMuPDF==1.23.0
numpy==1.24.3
scikit-learn==1.3.0
```

**Total size**: ∼50MB

---

## 🛠️ Docker Setup

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


## 🚧 Troubleshooting

* **Path Issues**: Ensure `PYTHONPATH=.` or use full imports
* **PDF Errors**: Check PDF paths and encodings
* **Docker**: Avoid `slim` base images

---

## 🚀 Success Criteria

| Goal              | Status |
| ----------------- | ------ |
| CPU-only          | ✅      |
| < 1GB Footprint   | ✅      |
| Dockerized        | ✅      |
| Generalized Logic | ✅      |
| High Relevance    | ✅      |

---

## 🎓 License

Created for Adobe India Hackathon 2025 — Challenge 1B.
**Built with efficiency, clarity, and precision in mind.**
