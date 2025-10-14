# Testing Guide

### Run all tests

```bash
pytest tests/
```
### Run specific tests
```bash
pytest tests/api/ -v              # API Mocked test
pytest tests/integration/ -v      # Integration test 
pytest tests/unit/ -v             # Unit test
```