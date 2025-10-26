# Frontend - LLM Tournament Widget

Next.js frontend for the LLM Tournament Widget application.

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Home page
│   ├── questions/         # Questions pages
│   └── templates/         # Templates page
├── components/            # React components
│   ├── questions/         # Question-related components
│   ├── templates/         # Template-related components
│   └── ui/               # Reusable UI components
├── lib/                   # Utility functions
├── types/                 # TypeScript type definitions
└── public/               # Static assets
```

## Features

- **Template Browsing:** View and compare different prompt templates
- **Question Submission:** Submit questions to test templates
- **Tournament Results:** View side-by-side comparisons of LLM outputs
- **Performance Charts:** Visualize latency, tokens, and quality metrics
- **Responsive Design:** Modern UI with Tailwind CSS

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **React:** 19
- **Styling:** Tailwind CSS 4
- **UI Components:** Radix UI
- **Charts:** Recharts
- **Language:** TypeScript

## Development

- Development server: `npm run dev`
- Build: `npm run build`
- Lint: `npm run lint`

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) for font optimization.
