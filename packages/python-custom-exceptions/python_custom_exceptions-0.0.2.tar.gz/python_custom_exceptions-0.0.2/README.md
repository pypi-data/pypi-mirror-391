# Python Custom Exceptions
A repository containing custom exception classes for Python projects. <br>
These exceptions are designed to provide more specific error handling and improve code readability. 
They can be easily integrated into any Python application to enhance error management. <br>

---

### Features
- ✅ Specific Exception Classes: Custom exceptions for various error scenarios.
- ✅ Improved Readability: Clearer error handling in code.
- ✅ Easy Integration: Simple to add to existing Python projects.
- ✅ Standardized Error Handling: Consistent approach to managing exceptions.
- ✅ Structured Hierarchy: Organized exception classes for better maintainability.

---

### Installation
```bash
pip install python-custom-exceptions
```

---

### Usage Examples
```python
import os
from python_custom_exceptions import DiagnosticInfo, IsNotExistException


class DiagnosticInfoTest(DiagnosticInfo):
    file_path: str


file_path = "test_dir"
os.mkdir(file_path)
if not os.path.exists(file_path):
    raise IsNotExistException(
        subject="Directory",
        diagnostic_info=DiagnosticInfoTest(
            file_path=file_path
        )
    )
```

---

### 🤝 Contributing
If you have a helpful tool, pattern, or improvement to suggest:
Fork the repo <br>
Create a new branch <br>
Submit a pull request <br>
I welcome additions that promote clean, productive, and maintainable development. <br>

---

### 🙏 Thanks
Thanks for exploring this repository! <br>
Happy coding! <br>
