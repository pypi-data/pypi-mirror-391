# gsearch-wrapper v0.3.0

A **modern Python package** providing a pluggable wrapper for **Google Search** — ready for API, scraping, and AI integration.

---

## 🧠 Functions Available

| Function | Description |
|-----------|--------------|
| `search(query, num=10)` | Returns placeholder SERP results |
| `get_related_queries(query)` | Returns related keywords |
| `get_featured_snippets(query)` | Fetches featured snippet placeholder |
| `get_top_domains(query)` | Lists placeholder top domains |
| `get_people_also_ask(query)` | Returns dummy PAA questions |
| `summarize_serp(query)` | Returns text summary placeholder |
| `cache_results(query)` | Simulates caching |
| `compare_queries(query1, query2)` | Compares SERP overlap |
| `export_to_csv(results, filename)` | Exports results to CSV |
| `visualize_serp(query)` | Describes visualization placeholder |

---

## 🚀 Uploading to PyPI (Modern Build)

### Step 1: Install dependencies
```bash
pip install build twine
```

### Step 2: Build your package
```bash
python -m build
```

### Step 3: Upload to TestPyPI
```bash
twine upload --repository testpypi dist/*
```

### Step 4: Test install
```bash
pip install -i https://test.pypi.org/simple/ gsearch-wrapper
```

### Step 5: Upload to official PyPI
```bash
twine upload dist/*
```

---

## 📄 License
MIT License © 2025 Amal Alexander
