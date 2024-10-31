# Pokemon TCG Analytics

A data analytics platform for the Pokemon Trading Card Game, providing meta game analysis, deck optimization, and trend predictions to compensate the game in real life or on Pokemon TCG Online.

## Features

- Meta game analysis and predictions
- Deck consistency analysis
- Card synergy identification
- Tournament trend tracking

## Technology Stack

- Backend: Python/FastAPI
- Database: PostgreSQL
- Analytics: pandas, numpy, scikit-learn
- API Integration: Pokemon TCG API, Limitless TCG

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/pokemon-tcg-analytics.git
cd pokemon-tcg-analytics
```

2. Create and activate virtual environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix or MacOS
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create .env file and add your Pokemon TCG API key
```
POKEMON_TCG_API_KEY=your_api_key_here
```

5. Run the application
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
pokemon-tcg-analytics/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   └── services/
├── tests/
└── requirements.txt
```

## Development

This project is under active development. Current focus areas:
- Setting up initial API structure
- Implementing data models
- Integrating external APIs
