# Wealth App 💰

A personal finance and mood tracking web application that helps users manage their expenses and monitor their emotional well-being.

## Features

- **Expense Tracking**: Add, edit, and categorize personal expenses
- **Mood Monitoring**: Track daily mood levels and emotional patterns
- **User Authentication**: Secure signup/login system
- **Dashboard**: Visualize financial and mood data
- **Responsive Design**: Works on desktop and mobile browsers

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database with async SQLAlchemy
- **Redis** - Caching and rate limiting
- **JWT Authentication** - Secure token-based auth
- **Advanced Patterns**: Rate limiting, retries, circuit breaker, queueing

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database and Redis URLs
```

5. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
wealth-app/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes and endpoints
│   │   ├── core/         # Core utilities (config, security, Redis, etc.)
│   │   ├── db/           # Database models and session
│   │   ├── schemas/      # Pydantic schemas
│   │   └── main.py       # FastAPI app
│   ├── tests/            # Backend tests
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── api/          # API client functions
│   │   ├── types/        # TypeScript types
│   │   └── App.tsx       # Main app component
│   └── package.json      # Node.js dependencies
└── README.md
```

## Development

### Backend Development
- The backend includes robust patterns: rate limiting, caching, retries, and circuit breakers
- Redis is used for caching and rate limiting
- All API endpoints are protected with JWT authentication
- Database operations use async SQLAlchemy

### Frontend Development
- Built with modern React and TypeScript
- Responsive design with Tailwind CSS
- API integration with axios
- Protected routes with authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
