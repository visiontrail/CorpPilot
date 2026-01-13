# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CostMatrix is an enterprise travel cost analysis platform that processes Excel files containing attendance and travel expense data, generates analytics dashboards, and exports reports.

## Development Commands

### Frontend (React + TypeScript + Vite)
```bash
cd frontend
npm run dev      # Start dev server on http://localhost:5173
npm run build    # Build for production
npm run lint     # Run ESLint
npm run preview  # Preview production build
```

### Backend (FastAPI + Python)
```bash
cd backend
python -m app.main      # Start server on http://localhost:8000
# Or with uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

### High-Level Data Flow

1. **Upload**: User uploads Excel file via frontend (`/api/upload`)
2. **Analysis**: Frontend calls `/api/analyze?file_path=...` with the uploaded file path
3. **Processing**: `ExcelProcessor` loads sheets, performs analysis, returns JSON
4. **Dashboard**: Frontend displays results with charts using ECharts
5. **Export**: Optional Excel export (appends new sheets) or PPT export

### Backend Structure

```
backend/app/
├── main.py              # FastAPI app entry point, CORS config
├── config.py            # Settings via pydantic-settings
├── api/
│   └── routes.py        # All API endpoints
├── models/
│   └── schemas.py       # Pydantic models for request/response
├── services/
│   ├── excel_processor.py    # Core data analysis logic
│   └── ppt_export_service.py # PowerPoint report generation
└── utils/
    ├── logger.py        # Centralized logging
    └── helpers.py       # Utility functions
```

### Frontend Structure

```
frontend/src/
├── App.tsx              # Router setup (React Router)
├── layouts/
│   └── MainLayout.tsx   # App layout with sidebar
├── pages/
│   ├── Dashboard.tsx    # Main analytics dashboard
│   └── Upload.tsx       # File upload page
├── services/
│   └── api.ts           # Axios client for backend API calls
└── types/
    └── index.ts         # TypeScript types matching backend schemas
```

## Key Implementation Details

### ExcelProcessor (`backend/app/services/excel_processor.py`)

The `ExcelProcessor` class handles all Excel data analysis. Key patterns:

- **Conditional Workbook Loading**: `load_all_sheets(load_workbook_obj=False)` - Only loads the openpyxl Workbook object when needed (e.g., for export). This significantly improves performance for analysis-only operations.
- **Caching**: Uses `_attendance_cache` and `_travel_cache` to avoid re-processing data across multiple analysis calls.
- **Project Code Extraction**: Parses project strings like `"05010013 市场-整星..."` to extract code (`05010013`) and name.
- **Top-N Aggregation**: `aggregate_project_costs(top_n=20)` and `calculate_department_costs(top_n=15)` return top N items plus an "其他" (Others) aggregation for remaining items.

### Required Excel Sheet Structure

Input files must contain these sheets:
- **状态明细**: Attendance data (日期, 姓名, 一级部门, 当日状态判断, 工时)
- **机票**: Flight bookings (授信金额, 项目, 预订人姓名, 差旅人员姓名, 出发日期, etc.)
- **酒店**: Hotel bookings (similar structure)
- **火车票**: Train tickets (similar structure)

### Cross-Validation Anomaly Detection

The `cross_check_attendance_travel()` method performs:
- **Type A (Conflict)**: Attendance shows "上班" (working) but travel expense exists on the same date
- Uses pandas merge on 姓名+日期 for efficient lookup, avoiding nested loops

### Excel Export Important Note

When exporting analysis results to Excel, the project **must use `openpyxl`** directly, NOT `pandas.to_excel()`. The `write_analysis_results()` method:
1. Loads the workbook with `openpyxl.load_workbook()`
2. Creates new sheets with analysis data
3. Preserves all original formatting, styles, and formulas
4. Saves to a new file

Using `pandas.to_excel()` would overwrite the entire file and lose formatting.

### API Proxy Configuration

Frontend dev server proxies `/api` requests to `http://localhost:8000` (see `vite.config.ts`). Set `VITE_API_URL` environment variable to override.

### Upload Records Persistence

Backend maintains `upload_records.json` in the upload directory tracking:
- File path, name, size, sheets
- Upload time
- Parse status (`parsed` boolean)
- Last analyzed timestamp

This allows users to see previously uploaded files and re-analyze them.

### Frontend State Management

- Uses React Router for page navigation
- Ant Design Pro Components for UI
- ECharts for data visualization
- Axios for API calls with 5-minute timeout for large file operations
