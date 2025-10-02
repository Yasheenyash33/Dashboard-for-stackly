# Training Management System

A comprehensive web application for managing training sessions, users, and analytics in an educational or corporate training environment. Built with modern web technologies for scalability and real-time collaboration.

## Features

### User Management
- **Role-based Access Control**: Admin, Trainer, and Trainee roles with different permissions
- **User Authentication**: Secure JWT-based authentication system
- **Profile Management**: Create, update, and delete user accounts

### Session Management
- **Training Sessions**: Schedule, update, and track training sessions
- **Real-time Updates**: WebSocket integration for live session status updates
- **Session Status Tracking**: Monitor scheduled, completed, and cancelled sessions

### Analytics & Reporting
- **User Analytics**: View user distribution by roles
- **Session Analytics**: Track session statistics by status
- **Dashboard Views**: Role-specific dashboards with relevant metrics

### Real-time Features
- **WebSocket Integration**: Live updates for session and user changes
- **Notifications**: Toast notifications for user actions

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **React Hot Toast** for notifications
- **Lucide React** for icons
- **Recharts** for data visualization

### Backend
- **FastAPI** for REST API
- **SQLAlchemy** with MySQL database
- **JWT** for authentication
- **WebSockets** for real-time updates
- **Pydantic** for data validation

## Prerequisites

Before running this application, make sure you have the following installed:

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **MySQL** (v5.7 or higher)
- **Git**

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd training-management-system
   ```

2. **Backend Setup:**

   a. Navigate to the backend directory:
   ```bash
   cd backend
   ```

   b. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   On Windows: venv\Scripts\activate
   ```

   c. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   d. Set up environment variables:
   Create a `.env` file in the backend directory:
   ```env
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=training_app
   SECRET_KEY=your-secret-key-here
   ```

3. **Frontend Setup:**

   a. Navigate to the root directory:
   ```bash
   cd ..
   ```

   b. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Database Setup

1. **Start MySQL service** and ensure it's running on your system.

2. **Create the database:**
   The application will automatically create the database and tables when you run the backend for the first time.

3. **Load sample data (optional):**
   ```bash
   cd backend
   python -m backend.sample_data
   if error shows
   backend\venv\Scripts\python.exe -m backend.sample_data
   ```

   This will create sample users and sessions for testing.

## Running the Application

1. **Start the Backend Server:**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py
   ```
   The backend will start on `http://localhost:8001`

2. **Start the Frontend Development Server:**
   ```bash
   # In a new terminal, from the root directory
   npm run dev
   ```
   The frontend will start on `http://localhost:5173`

3. **Access the Application:**
   Open your browser and navigate to `http://localhost:5173`

## Sample Login Credentials

After running the sample data script, you can use these credentials:

- **Admin:**
  - Username: `admin`
  - Password: `admin123`

- **Trainer:**
  - Username: `john_trainer`
  - Password: `trainer123`

- **Trainee:**
  - Username: `alice_trainee`
  - Password: `trainee123`

## API Documentation

The FastAPI backend provides automatic API documentation at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

### Key Endpoints

- `POST /auth/login` - User authentication
- `GET /users/` - List users (admin/trainer only)
- `POST /users/` - Create user (admin only)
- `GET /sessions/` - List sessions
- `POST /sessions/` - Create session (admin/trainer)
- `GET /analytics/users` - User analytics (admin only)
- `GET /analytics/sessions` - Session analytics (admin only)
- `WebSocket /ws` - Real-time updates

## Project Structure

```
training-management-system/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── database.py          # Database configuration
│   ├── sample_data.py       # Sample data script
│   └── requirements.txt     # Python dependencies
├── src/
│   ├── components/          # React components
│   │   ├── Auth/           # Authentication components
│   │   ├── Dashboard/      # Dashboard components
│   │   ├── Layout/         # Layout components
│   │   ├── Sessions/       # Session management
│   │   ├── Users/          # User management
│   │   ├── Analytics/      # Analytics components
│   │   └── Settings/       # Settings components
│   ├── contexts/           # React contexts
│   ├── App.jsx             # Main app component
│   └── main.jsx            # App entry point
├── public/                 # Static assets
├── index.html              # HTML template
├── package.json            # Node dependencies
├── vite.config.ts          # Vite configuration
└── README.md               # This file
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Backend Development

- The backend uses auto-reload when running `python main.py`
- Database schema changes require manual migration or dropping/recreating tables

### Environment Variables

#### Backend (.env)
- `DB_USER` - MySQL username
- `DB_PASSWORD` - MySQL password
- `DB_HOST` - MySQL host (default: localhost)
- `DB_PORT` - MySQL port (default: 3306)
- `DB_NAME` - Database name (default: training_app)
- `SECRET_KEY` - JWT secret key

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or create an issue in the repository.
