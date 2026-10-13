# AegisCare - Heart Disease Analytics Platform

A comprehensive healthcare analytics platform for analyzing heart disease datasets and providing insights through an interactive dashboard.

## Features

- **CSV Data Processing**: Upload and process heart disease datasets (e.g., merged_heart_10k.csv)
- **Real-time Analytics**: Interactive dashboard with key metrics and visualizations
- **Patient Management**: Comprehensive patient database with heart disease vitals
- **Trend Analysis**: Patient vitals trends over time with interactive charts
- **Data Export**: Export patient data in multiple formats (CSV, Excel, JSON)
- **Secure API**: RESTful backend with authentication and role-based access

## Dataset Structure

The system is designed to work with heart disease datasets containing the following fields:

- `patient_id`: Unique patient identifier
- `patient_name`: Patient's full name
- `phone`: Contact phone number
- `age`: Patient age
- `sex`: Gender (0=M, 1=F)
- `chest pain type`: Type of chest pain (0-3)
- `Resting blood pressure`: Blood pressure in mmHg
- `Serum cholesterol level (mg/dl)`: Cholesterol level
- `Fasting Blood Sugar`: Blood sugar level
- `Resting Electrocardiogram Results`: ECG results (0-2)
- `Maximum Heart Rate Achieved`: Maximum heart rate
- `Exercise-Induced Angina`: Exercise angina (0/1)
- `ST Depression Induced by Exercise`: ST depression
- `Slope of the Peak Exercise ST Segment`: ST slope (0-2)
- `Number of Major Vessels Colored by Fluoroscopy`: Number of vessels
- `Thalassemia`: Thalassemia type (0-3)
- `target`: Heart disease presence (0/1)

## Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Node.js 16+ (for frontend)

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd aegisCare/backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the backend directory:

   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=aegiscare
   JWT_SECRET=your_secret_key
   ```

5. **Initialize Database**

   ```bash
   python init_db.py
   ```

6. **Start Backend Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd ../frontend
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start Streamlit App**
   ```bash
   streamlit run Home.py
   ```

## Project Structure

```
aegisCare/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routers/
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── dashboard.py     # Dashboard data endpoints
│   │   │       ├── patients.py      # Patient management endpoints
│   │   │       └── uploads.py       # CSV upload endpoints
│   │   ├── db/
│   │   │   ├── connection.py        # Database connection
│   │   │   ├── repo.py             # Data repository functions
│   │   │   ├── queries.py          # SQL queries
│   │   │   └── schema.sql          # Database schema
│   │   ├── services/
│   │   │   └── ingest.py           # CSV data ingestion
│   │   └── main.py                 # FastAPI application
│   ├── init_db.py                  # Database initialization
│   └── requirements.txt             # Python dependencies
├── frontend/
│   ├── pages/
│   │   ├── 1_Dashboard_overview.py     # Main dashboard
│   │   ├── 2_Patient_vital_trends.py   # Patient vitals trends
│   │   ├── 5_Seed_Data.py              # Patient management & upload
│   │   └── ...                         # Other pages
│   ├── components/                      # Reusable components
│   ├── utils/                          # Utility functions
│   └── Home.py                         # Main Streamlit app
├── data/
│   └── merged_heart_10k.csv            # Sample heart disease dataset
└── README.md
```

## Authentication

The system uses session-based authentication with the following default credentials:

- **Email**: admin@aegiscare.com
- **Password**: password123

## Usage Guide

### 1. Data Upload

1. Navigate to the "Patient Data Management" page
2. Click "Choose a CSV file" and select your heart disease dataset
3. Click "Process Data" to upload and process the CSV
4. The system will automatically parse and store the data

### 2. Dashboard Overview

The main dashboard displays:

- Total patients and observations
- Gender distribution
- Average age and blood pressure
- Heart disease statistics
- Vitals distribution charts

### 3. Patient Vitals Trends

- Select a patient from the dropdown
- View current vital signs
- Analyze trends over time
- Interactive charts for different vital parameters

### 4. Patient Management

- View all patients in a comprehensive table
- Search patients by name or ID
- Export patient data in various formats
- Detailed patient information and vitals

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Dashboard

- `GET /dashboard/stats` - Dashboard statistics
- `GET /dashboard/vitals-summary` - Vitals summary
- `GET /dashboard/recent-activity` - Recent activity

### Patients

- `GET /patients/` - List all patients
- `GET /patients/search` - Search patients
- `GET /patients/{id}` - Get patient details
- `GET /patients/{id}/vitals` - Get patient vitals

### Uploads

- `POST /uploads/csv` - Upload CSV file

## Data Processing

The system processes CSV data through the following pipeline:

1. **File Upload**: CSV file uploaded via web interface
2. **Data Parsing**: CSV parsed and validated
3. **Patient Creation**: New patients added to database
4. **Vitals Storage**: Heart disease vitals stored in summary table
5. **Observations**: Detailed observations stored for trend analysis
6. **Dashboard Update**: Real-time dashboard metrics updated

## Troubleshooting

### Common Issues

1. **Database Connection Error**

   - Verify MySQL service is running
   - Check database credentials in `.env` file
   - Ensure database `aegiscare` exists

2. **CSV Upload Fails**

   - Verify CSV format matches expected structure
   - Check file encoding (should be UTF-8)
   - Ensure all required columns are present

3. **Frontend Not Loading**

   - Verify backend is running on port 8000
   - Check API endpoint responses
   - Review browser console for errors

4. **Database Schema Error: "Key column 'target' doesn't exist in table"**
   - This error occurs when the database schema is outdated
   - **Solution 1 (Recommended)**: Run the migration script:
     ```bash
     cd backend
     python migrate_db.py
     ```
   - **Solution 2 (If migration fails)**: Reset the database completely:
     ```bash
     cd backend
     python reset_db.py
     ```
   - **Solution 3**: Manually update the database:
     ```sql
     ALTER TABLE patient_vitals_summary
     ADD COLUMN target INT NULL COMMENT 'Heart disease (1=yes, 0=no)';
     ```

### Database Schema Issues

If you encounter database schema errors, the system provides three solutions:

1. **Migration Script** (`migrate_db.py`): Updates existing database without losing data
2. **Reset Script** (`reset_db.py`): Completely recreates database (WARNING: loses all data)
3. **Manual SQL**: Direct database commands for advanced users

### Logs

- Backend logs are displayed in the terminal running uvicorn
- Frontend errors appear in the Streamlit interface
- Database errors are logged in the backend console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section above

## Future Enhancements

- Machine learning models for heart disease prediction
- Advanced analytics and reporting
- Integration with electronic health records
- Mobile application
- Real-time patient monitoring
- Advanced visualization options

---

**AegisCare** - Protecting hearts through data-driven insights.
