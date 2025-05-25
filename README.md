# Climate Hazard Analysis Web Application

## Overview
This is a full-stack web application designed to analyze climate hazards such as heatwaves, floods, droughts, and heavy rainfall across various regions of India. It provides an interactive map interface, supports statistical trend detection, and allows users to export insights for further analysis.

## Features
- Region selection via an interactive map (custom or predefined areas)
- Display of historical hazard trends including frequency and intensity
- Application of statistical methods: Linear Regression and Mann-Kendall trend test
- Export of results in CSV and PDF formats
- Automatic threshold adjustment based on hazard type

## Tech Stack
- Frontend: React.js, Leaflet, Recharts
- Backend: FastAPI, Python, Pandas, SciPy
- Styling: Custom CSS (App.css)
- Data Source: Open-Meteo Weather API

## Live Application
Link: [https://your-deployment-url.com](https://your-deployment-url.com)  
(Replace with actual hosted URL on platforms like Vercel, Netlify, or Render)

## Local Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Directory Structure

```
/frontend
  - App.jsx
  - App.css
  - components/
  - utils/api.js

/backend
  - main.py
  - climate_logic.py
  - climate_hazard_detection.py
  - report_utils.py
```

## License
MIT License