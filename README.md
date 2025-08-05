# Group SMS Chat Application

A modern web application that enables group chat functionality over SMS, built with FastAPI (Python) backend and React frontend.

## Features

- **User Management**: Register/login with phone number
- **Group Management**: Create, search, join, and leave groups
- **SMS Integration**: Send and receive group messages via SMS using Twilio
- **Real-time Updates**: Auto-refresh messages in the web interface
- **Multi-group Support**: Users can participate in multiple groups simultaneously

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL/SQLite
- **Frontend**: React, React Router, Axios
- **SMS Service**: Twilio API
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional, recommended)
- Twilio Account (for SMS functionality)

## Quick Start

### Option 1: Using Make (Recommended for local development)

```bash
# First time setup
make install
cp backend/.env.example backend/.env
# Edit backend/.env with your Twilio credentials

# Run the application
make run
```

Available make commands:
- `make help` - Show all available commands
- `make demo` - Quick demo setup with sample data
- `make run` - Run both backend and frontend
- `make test` - Run tests (including task requirement validation)
- `make seed-demo` - Add sample users, groups, and messages
- `make clean` - Clean up generated files

For a quick demo:
```bash
make demo  # Sets up everything with sample data
make run   # Start the application
```

### Option 2: Using Docker Compose

```bash
docker-compose up --build
```

### Option 3: Manual Setup

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Update .env with your Twilio credentials
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup** (in a new terminal):
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Setting Up Twilio

### Option 1: Mock Mode (For Development)
Add this to your `.env` file to run without Twilio:
```
MOCK_SMS=true
```
This will log SMS messages to the console instead of sending them.

### Option 2: Real Twilio Integration
1. Create a Twilio account at https://www.twilio.com (free trial includes $15 credit)
2. Get a phone number capable of sending/receiving SMS
3. Add your credentials to `.env`:
   - `TWILIO_ACCOUNT_SID` - Your account SID (from Twilio Console)
   - `TWILIO_AUTH_TOKEN` - Your auth token (from Twilio Console)
   - `TWILIO_PHONE_NUMBER` - Your Twilio phone number
4. Configure webhook for incoming messages:
   - In Twilio Console, go to your phone number settings
   - Set the webhook URL to: `http://your-domain.com/api/sms/webhook`
   - Method: POST
   - For local testing, use ngrok: `ngrok http 8000`

## Usage

1. **Register**: Create an account with your name and phone number
2. **Browse Groups**: Search and view available groups
3. **Join Groups**: Click "Join Group" to participate
4. **Send Messages**: Reply to the SMS you receive after joining
5. **Multi-group Messaging**: Use `@groupname message` format when in multiple groups

## API Endpoints

- `POST /api/users/` - Create new user
- `GET /api/users/` - List all users
- `GET /api/groups/` - List/search groups
- `POST /api/groups/` - Create new group
- `POST /api/groups/{id}/join/{user_id}` - Join group
- `POST /api/groups/{id}/leave/{user_id}` - Leave group
- `GET /api/groups/{id}/messages` - Get group messages
- `POST /api/sms/webhook` - Twilio webhook endpoint

## Development

The application uses:
- **Hot Reload**: Both backend and frontend support hot reloading
- **CORS**: Configured for local development
- **Database**: PostgreSQL in production, SQLite for quick local testing

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment Considerations

- Use environment variables for all sensitive data
- Set up proper HTTPS for production
- Configure Twilio webhook with your production URL
- Use a production-grade database (PostgreSQL recommended)
- Implement rate limiting for SMS endpoints
- Add authentication middleware for API endpoints