# License Plate Marketplace

A web application for buying and selling license plates, built with Flask and React.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- MySQL 8.0 or higher
- Node.js 14.0 or higher
- npm (Node Package Manager)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd IS499MYSQL
```

### 2. Create and Activate Virtual Environment
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
1. Create a MySQL database:
```sql
CREATE DATABASE license_plate_marketplace;
```

2. Configure database connection:
   - Create a `.env` file in the root directory
   - Add the following configuration:
```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=license_plate_marketplace
SECRET_KEY=your_secret_key
```

3. Run database migrations:
```bash
flask db upgrade
```

### 5. Frontend Setup
1. Install Node.js dependencies:
```bash
cd static
npm install
```

2. Build the frontend:
```bash
npm run build
```

## Running the Application

### Development Mode
1. Start the Flask server:
```bash
flask run
```

2. In a separate terminal, start the React development server:
```bash
cd static
npm start
```

The application will be available at:
- Backend: http://localhost:5000
- Frontend: http://localhost:3000

### Production Mode
1. Build the frontend:
```bash
cd static
npm run build
```

2. Start the Flask server:
```bash
flask run --host=0.0.0.0
```

## Project Structure
```
IS499MYSQL/
├── migrations/           # Database migrations
├── static/              # Static files
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── img/            # Images
├── templates/           # HTML templates
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Features
- User authentication (login/signup)
- License plate listings
- User profiles
- Admin dashboard
- Payment processing
- Wishlist functionality
- Order history

## Security Considerations
- Never commit the `.env` file
- Keep your database credentials secure
- Use strong passwords for admin accounts
- Regularly update dependencies

## Troubleshooting
1. If you encounter database connection issues:
   - Verify your MySQL service is running
   - Check your `.env` file credentials
   - Ensure the database exists

2. If frontend build fails:
   - Clear node_modules: `rm -rf node_modules`
   - Reinstall dependencies: `npm install`
   - Try building again: `npm run build`

## Support
For any issues or questions, please contact the development team.

## License
[Your License Here] 