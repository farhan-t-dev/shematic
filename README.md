# Insurance Schematic Builder

A minimalist, high-performance web application designed to transform complex insurance program spreadsheets into professional PowerPoint schematics. Built with a focus on precision, security, and a distilled "stupid simple" user experience.

![UI Aesthetic](https://via.placeholder.com/800x400?text=Minimalist+UI+Design)

## ⚡ Key Features

- **Automated Ingestion**: Intelligent parsing of `.xlsx` files to detect layers, attachment points, and carrier participation.
- **Deep Validation**: Comprehensive logic engine that flags program gaps, duplicate layers, and fuzzy carrier name mismatches.
- **High-Fidelity Rendering**: Programmatically generates polished PowerPoint decks using `python-pptx` with color-coded layouts.
- **Minimalist UX**: A focused, single-screen workflow designed for maximum efficiency and zero learning curve.
- **Enterprise Security**: Session-based authentication and automatic cleanup of temporary data.

## 🛠 Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS.
- **Backend**: FastAPI (Python 3.10+).
- **Core Engine**: Openpyxl (Excel Parsing) and Python-PPTX (PowerPoint Rendering).
- **Styling**: Modern minimalist aesthetic with extra-bold typography.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/str-schematic-modern.git
cd str-schematic-modern

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r scripts/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your desired credentials

# Start the API server
python backend/main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install

# Start development server
npm run dev
```
The app will be available at `http://localhost:5173`.

## ⚙️ Configuration

The application is configured via environment variables in the root `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_USERNAME` | Login username | `admin` |
| `ADMIN_PASSWORD` | Login password | `admin1234` |
| `SESSION_TTL_SECONDS` | Auth session duration | `28800` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:5173` |

## 🧪 Testing

Run the Python test suite to verify the parsing and validation logic:
```bash
python -m unittest discover -s tests -v
```

## 📄 License

This project is proprietary and confidential. All rights reserved by RPS Insurance Services.
