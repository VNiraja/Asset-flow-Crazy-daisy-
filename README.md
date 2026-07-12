# AssetFlow - Authentication Module

A complete, production-ready authentication system for the AssetFlow Asset Management Platform. Built with Python, Streamlit, SQLite3, and bcrypt.

## Features

### Authentication
- ✅ **User Registration** - Secure signup with comprehensive validation
- ✅ **User Login** - Email and password authentication with bcrypt hashing
- ✅ **Session Management** - Persistent session state using Streamlit
- ✅ **Password Hashing** - Industry-standard bcrypt algorithm
- ✅ **Email Validation** - Regex-based email format validation
- ✅ **Password Strength** - Enforced password requirements
- ✅ **Logout** - Secure session cleanup

### Role-Based Access Control
- 🔐 **Admin Role** - Full access to all features including user management
- 👤 **Employee Role** - Limited access to dashboard only
- 🔒 **Authorization Checks** - Prevent unauthorized access to restricted pages

### User Management
- 📋 **User Dashboard** - View personal account information
- 👥 **User Management** - Admin panel for managing all users
- 📊 **User Statistics** - View user distribution and recent registrations
- 🔧 **Role Assignment** - Change user roles (admin only)
- 🗑️ **User Deletion** - Remove users from the system (admin only)

### Database
- 🗄️ **SQLite Database** - Lightweight and reliable data storage
- 🔄 **Auto-Initialization** - Automatic database and table creation
- 📝 **User Table** - Stores user information with proper schema

### Security
- 🔐 **Password Hashing** - bcrypt with 12 rounds
- ✅ **Duplicate Prevention** - Unique email constraint
- 🛡️ **Input Validation** - Comprehensive validation of all inputs
- 🚫 **Unauthorized Access Prevention** - Role-based access control

### User Interface
- 🎨 **Professional Design** - Modern Streamlit interface
- 📱 **Responsive Layout** - Works on desktop and mobile
- 🎯 **Centered Forms** - Clean login and signup forms
- 🧭 **Sidebar Navigation** - Easy navigation between pages
- 📊 **Data Tables** - Organized user information display
- ✨ **Visual Feedback** - Success and error messages

## Project Structure

```
assetflow/
│
├── app.py                    # Main application entry point
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── assetflow.db             # SQLite database (auto-created)
│
├── utils/
│   ├── __init__.py
│   ├── db.py               # Database operations
│   ├── auth.py             # Authentication functions
│   └── validators.py       # Input validation
│
├── pages/
│   ├── __init__.py
│   ├── login.py            # Login page
│   ├── signup.py           # Registration page
│   ├── dashboard.py        # User dashboard
│   └── admin.py            # Admin panel
│
└── assets/                  # Static assets directory
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the project**
   ```bash
   cd assetflow
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

The application will automatically:
- Create the SQLite database (`assetflow.db`)
- Create the required database tables
- Open in your default browser at `http://localhost:8501`

## Usage

### First-Time Setup

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Create an account**
   - Click "Sign Up Here"
   - Enter your full name
   - Enter a valid email address
   - Create a secure password meeting all requirements
   - Confirm your password
   - Click "Create Account"

3. **Login**
   - Enter your email address
   - Enter your password
   - Click "Login"

### Password Requirements

Your password must contain:
- **Minimum 8 characters** in length
- **At least 1 uppercase letter** (A-Z)
- **At least 1 lowercase letter** (a-z)
- **At least 1 digit** (0-9)
- **At least 1 special character** (!@#$%^&*(),.?":{}|<>)

**Example:** `SecurePass123!`

### User Roles

#### Employee Role
- Access to personal dashboard
- View account information
- View login time and email
- Cannot access admin features

#### Admin Role
- Access to all employee features
- Full admin panel access
- View all registered users
- Change user roles
- Delete users
- View user statistics

### Features by Page

#### Login Page (`/`)
- Email and password input
- Form validation
- Session creation
- Link to signup page

#### Signup Page
- Full name input
- Email input
- Password input
- Password confirmation
- Password requirements guide
- Comprehensive validation
- Duplicate email prevention

#### Dashboard
- Welcome message with username
- Account information display
- Account details (name, email)
- Access information (role, login time)
- Quick stats
- Available features list
- Session information
- Logout button

#### Admin Panel
- **Users Tab**
  - List all registered users
  - Display user information
  - Show user count by role
  
- **Statistics Tab**
  - Total users metric
  - Admin count metric
  - Employee count metric
  - Role distribution chart
  - Recent registrations list
  
- **Management Tab**
  - Select user for management
  - Change user roles
  - Delete users
  - Prevent self-management

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL
)
```

**Columns:**
- `user_id` - Unique identifier (UUID)
- `full_name` - User's full name
- `email` - User's email (unique constraint)
- `password` - Hashed password (bcrypt)
- `role` - User role (admin/employee)
- `created_at` - Account creation timestamp (ISO format)

## API Reference

### Authentication Module (`utils/auth.py`)

#### `AuthManager.signup(full_name, email, password)`
Register a new user.
- **Returns:** (success: bool, message: str)

#### `AuthManager.login(email, password)`
Authenticate user login.
- **Returns:** (success: bool, message: str, user_data: dict)

#### `AuthManager.hash_password(password)`
Hash a password using bcrypt.
- **Returns:** (hashed_password: str)

#### `AuthManager.verify_password(password, hashed_password)`
Verify password against hash.
- **Returns:** (match: bool)

### Validators Module (`utils/validators.py`)

#### `validate_email(email)`
Validate email format.
- **Returns:** (is_valid: bool, error_message: str)

#### `validate_password(password)`
Validate password strength.
- **Returns:** (is_valid: bool, error_message: str)

#### `validate_full_name(full_name)`
Validate full name.
- **Returns:** (is_valid: bool, error_message: str)

### Database Module (`utils/db.py`)

#### `Database.create_user(user_id, full_name, email, password_hash, role, created_at)`
Create a new user in database.
- **Returns:** (success: bool, message: str)

#### `Database.get_user_by_email(email)`
Retrieve user by email.
- **Returns:** (user_data: dict or None)

#### `Database.get_all_users()`
Retrieve all users.
- **Returns:** (users: list of dict)

#### `Database.delete_user(user_id)`
Delete a user.
- **Returns:** (success: bool, message: str)

#### `Database.update_user_role(user_id, new_role)`
Update user's role.
- **Returns:** (success: bool, message: str)

## Error Handling

The application includes comprehensive error handling for:
- **Database Errors** - Connection and query failures
- **Duplicate Users** - Email already registered
- **Invalid Login** - Incorrect credentials
- **Empty Fields** - Required field validation
- **Invalid Email** - Email format validation
- **Weak Password** - Password requirement validation
- **Session Errors** - Session state issues

## Security Features

1. **Password Security**
   - bcrypt hashing with 12 rounds
   - Strong password requirements
   - No plaintext storage

2. **Database Security**
   - Email unique constraint
   - Input sanitization
   - SQL injection prevention (using parameterized queries)

3. **Session Security**
   - Streamlit session state isolation
   - Automatic logout capability
   - Role-based access control

4. **Input Validation**
   - Email format validation (regex)
   - Password strength validation (regex)
   - Full name validation
   - Comprehensive error messages

## Troubleshooting

### Database Issues
- **Issue:** "Database initialization error"
  - **Solution:** Ensure write permissions in the project directory
  - **Solution:** Delete `assetflow.db` and restart the app

### Login Issues
- **Issue:** "Invalid email or password"
  - **Solution:** Verify email and password are correct
  - **Solution:** Check caps lock is off

### Signup Issues
- **Issue:** "Email already registered"
  - **Solution:** Use a different email address
  - **Solution:** Check if the email was already used

- **Issue:** "Password must contain..."
  - **Solution:** Review password requirements
  - **Solution:** Ensure password has uppercase, lowercase, digit, and special character

### Port Already in Use
- **Issue:** "Port 8501 is already in use"
  - **Solution:** Stop other Streamlit instances
  - **Solution:** Use: `streamlit run app.py --server.port 8502`

## Technology Stack

- **Python** 3.10+
- **Streamlit** 1.28.1 - Web application framework
- **SQLite3** - Database
- **bcrypt** 4.1.1 - Password hashing
- **pandas** 2.1.3 - Data manipulation
- **uuid** - Unique user ID generation
- **re** - Regular expressions for validation
- **datetime** - Timestamp management

## Development

### Project Layout
- **utils/** - Core utilities and business logic
- **pages/** - Streamlit page components
- **assets/** - Static assets
- **app.py** - Main application router

### Adding New Features

1. **Create new validator** in `utils/validators.py`
2. **Add database functions** in `utils/db.py`
3. **Create page** in `pages/new_page.py`
4. **Add navigation** in `app.py`

## Performance

- Lightweight SQLite database
- Efficient bcrypt hashing (12 rounds)
- Optimized Streamlit session management
- Fast email and password validation
- Minimal dependencies

## Browser Compatibility

- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅
- Opera ✅

## Known Limitations

1. Single-user login per session
2. No email verification required
3. No password reset functionality
4. No two-factor authentication
5. No API endpoints (Streamlit only)

## Future Enhancements

- Email verification
- Password reset functionality
- Two-factor authentication
- API endpoints
- Advanced user filters
- User activity logging
- Audit trails
- Export user data

## License

This project is provided as-is for educational and commercial use.

## Support

For issues, questions, or suggestions, please check:
- Application error messages
- Database file permissions
- Python version compatibility
- Dependency installation

## Version

**AssetFlow v1.0** - Authentication Module

---

**Built with ❤️ using Streamlit**

For more information about Streamlit, visit: https://streamlit.io
