# 🧩 pylint-docstring-checker

A **Pylint plugin** that checks Python docstrings for **Google Python Style Guide** compliance  
and detects **non-English (Vietnamese) docstrings**.

This plugin helps teams enforce consistent documentation and quality across Python projects.

---

## ✨ Features

✅ **Google Python Style Guide** validation:
- Checks for correct `Args:`, `Returns:`, and `Raises:` sections.  
- Ensures the **summary line** exists, starts with a capital letter, and ends with a period.  
- Requires a blank line between summary and detail sections (PEP-257 friendly).  

🈲 **Language detection**:
- Warns if a docstring contains Vietnamese characters.

📊 **Summary report** at the end of each Pylint run:
```
📊 Docstring Summary Report:
- Total functions:                 10
- With docstring:                  8
- Without docstring:               2
- Vietnamese docstrings:           1
- English/Japanese docstrings:     7
- Google-style compliant:          4
- Google Style Coverage:           50.00%
- Coverage:                        80.00%
```

---

## 🛠️ Installation

### From PyPI
```bash
pip install pylint-docstring-checker
```
---

## 🚀 Usage

### Run directly
```bash
pylint --load-plugins=pylint_docstring_checker your_module.py
```

### Or enable in `.pylintrc`
```ini
[MASTER]
load-plugins=pylint_docstring_checker
```

Then simply run:
```bash
pylint your_project/
```

