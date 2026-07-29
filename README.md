# AI Financial Intelligence Platform

An AI-powered financial intelligence platform for analyzing and processing financial data.

## Project Setup

### Prerequisites
- Python 3.9+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/vengatc/ai-financial-intelligence-platform.git
cd ai-financial-intelligence-platform
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python -m src.main
```

### Running Tests

```bash
pytest tests/
```

## Project Structure

```
ai-financial-intelligence-platform/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

## License

MIT