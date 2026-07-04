# Multi-Agent Collaboration System

## Quick Start

1. Make sure .env file is configured with your API key
2. Install dependencies: pip install -r requirements.txt
3. Run command line: python main.py "your question"
4. Or run web interface: streamlit run app.py

## Architecture

User Question -> Researcher -> Analyst -> Writer -> Reviewer -> Final Article

## Agents

- Researcher: Gathers and organizes information
- Analyst: Analyzes research data and generates reports
- Writer: Writes articles based on analysis
- Reviewer: Reviews article quality and provides feedback

## Configuration

Edit .env file:
- OPENAI_API_KEY: Your API key
- OPENAI_MODEL: Model name (e.g., glm-4-flash)
- OPENAI_BASE_URL: API endpoint

## Testing

Run a test: python -c "from core.graph import run_workflow; result = run_workflow('Test question'); print(result.get('draft', 'None')[:100])"
