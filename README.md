# LLM Tournament Widget

A monorepo application for running tournaments between different LLM prompt templates. This project consists of a FastAPI backend and a Next.js frontend that allows users to test and compare various prompt engineering strategies.

## 🏗️ Project Structure

```
.
├── backend/          # FastAPI backend (Python)
├── frontend/         # Next.js frontend (TypeScript/React)
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+**
- **Node.js 18+**
- **npm** or **yarn**
- **OpenAI API Key**

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies using uv (recommended) or pip:**
   
   **Using uv (recommended):**
   ```bash
   # Install uv if you don't have it
   pip install uv
   
   # Install dependencies
   uv sync
   ```
   
   **Using pip:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Initialize the database and seed templates:**
   ```bash
   # Run seed script to create database and add default templates
   python seed.py
   ```

5. **Run the backend server:**
   ```bash
   # Using uv
   uv run main.py
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

   The frontend will be available at `http://localhost:3000`

## 📖 Usage

1. **Start both servers** (backend on port 8000, frontend on port 3000)
2. **Open your browser** to `http://localhost:3000`
3. **Browse templates** to see available prompt templates
4. **Ask a question** to start a tournament and compare different prompt strategies
5. **View comparisons** to see which template performs best

## 🏛️ Architecture

### Backend (FastAPI)
- **Framework:** FastAPI
- **Database:** SQLite with SQLModel ORM
- **LLM:** OpenAI GPT-4o-mini
- **Features:**
  - Template management
  - Question processing
  - LLM output generation
  - Performance tracking and analytics

### Frontend (Next.js)
- **Framework:** Next.js 16 (App Router)
- **UI:** React 19 with Tailwind CSS
- **Components:** Radix UI components
- **Features:**
  - Template browsing
  - Question submission
  - Tournament results visualization
  - Performance charts (Recharts)

## 🗃️ Database

The application uses SQLite with the following models:
- **Template:** Prompt templates with different strategies
- **Question:** User-submitted questions
- **Generation:** LLM outputs for each template/question pair
- **Duel:** Tournament results comparing templates

## 🔧 Development

### Backend
- Run with auto-reload: `python main.py`
- API docs available at: `http://localhost:8000/docs`
- Seed templates: `python seed.py`

### Frontend
- Development server: `npm run dev`
- Build for production: `npm run build`
- Start production server: `npm start`

## 📝 API Endpoints

- `GET /` - Welcome message
- `GET /templates/` - Get all templates
- `GET /templates/performance` - Get performance data
- `POST /questions/` - Submit a new question
- `GET /questions/` - Get all questions
- `GET /questions/{id}` - Get question details

## 🌟 Features

- **Multiple Prompt Strategies:** Test different prompting techniques
- **Performance Analytics:** Track latency, tokens, and quality metrics
- **Tournament System:** Compare multiple templates side-by-side
- **Responsive UI:** Modern, accessible interface with charts and visualizations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is part of the HippocraticAI Assessment.
