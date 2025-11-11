# Kystdatahuset Python Library

`kystdatahuset-python-lib` — Python SDK companion for the Kystdatahuset API

`kystdatahuset-python-lib` is the official Python client for accessing the **Kystdatahuset API**, a unified data and knowledge platform for coastal and maritime spatial analytics. 

It provides a clean, Pythonic, and strongly typed interface for querying datasets, managing authentication, and performing efficient data access.

---

## ✨ Features

### 🚀 Easy Installation  
Install directly from PyPI:

```bash
pip install kystdatahuset-python-lib
```

Supports Python **3.9+** on Linux, macOS, and Windows.

---

### 🔐 Simple Authentication  
The client offers:

- API key authentication  
- Support for headless servers and notebooks

Example:

```python
from kystdatahuset.auth import login
import os

    login_response = login("username", "password")
    jwt = auth_res.data.JWT
    voyages = get_voyages_for_ships_by_mmsi(
        auth_jwt=jwt,
        mmsi_ids=[258090000, 259028000],
        start_date=datetime(2024,1,1),
        end_date=datetime(2024,5,1),
    )

```
---

## 🌍 Efficient & “Social” Data Access

Instead of fetching massive multi-GB extracts, the library is designed for **smart, cooperative usage patterns**, where users share infrastructure responsibly:

### ✅ Time Window Batching  
Fetch long time periods in small, safe slices, python/Pandas "periods"


### ✅ Geographic Slicing  
Request only the needed spatial extent by WKT filters

---

## 🧱 Library Structure

```
+---kystdatahuset
|   |   ais.py
|   |   api_client.py
|   |   auth.py
|   |   const.py
|   |   file_storage.py
|   |   logging.py
|   |   voyage.py
|   |   __init__.py
|   |
|   +---models
|   |   |   AuthData.py
|   |   |   FileListing.py
|   |   |   WebServiceResponse.py
|   |   |   __init__.py
|   |   |
|   |
|   +---types
|   |   |   PandasFrequency.py
|   |   |   UploadFileType.py
|   |   |   __init__.py
|   |   |
|   |
|   +---utils
|   |   |   _date_range.py
|   |   |   __init__.py
```

---

## 📦 Development & Distribution

`kystdatahuset-py` uses standard packaging:

- `pyproject.toml` + `PEP 621` metadata  
- versioning via Semantic Versioning  
- full type hints (mypy-friendly)  
- GitHub Actions for automated testing & publishing   

---

## 🧠 Typical Use Cases

- Query live AIS vessel data efficiently  
- Retrieve spatial datasets in bounded windows  
- Build dashboards, decision-support tools, or AI/ML pipelines  
- Avoid oversized extracts by using time/space batching helpers  

---

## 📄 License

Open source under the **MIT License**.

