# Tests

This folder will contain automated tests for:

- backend API routes
- analysis services
- validation rules
- future frontend behavior when applicable

## Run tests

From the project root:

```bash
pytest
```

On Windows, when using the local `.venv`, install the pinned project dependencies
and run the suite with:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest
```
