### **README for Unified Automotive Retail Experience Application**

---

## **Unified Automotive Retail Experience**

This is a Flask-based web application designed to streamline dealership operations by integrating inventory management, sales tracking, and service scheduling. The platform enables admins, sales staff, service staff, and customers to manage and interact with dealership functionalities efficiently.

---

## **Project Structure**

```
Unified Automotive Retail Experience
│
├── flaskapp/                # Main application folder
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Core routes for the application
│   ├── static/              # Static files (CSS, images)
│   │   ├── profile_pics/    # Profile pictures upload folder
│   │   └── main.css         # Main application styles
│   ├── templates/           # HTML templates
│   │   ├── about.html       # About page
│   │   ├── account.html     # User account page
│   │   ├── add_sale.html    # Add sales form
│   │   ├── add_vehicle.html # Add new vehicle form
│   │   ├── book_service.html # Book a service appointment
│   │   ├── customer_service_data.html # Customer's service history
│   │   ├── edit_vehicle.html # Edit vehicle details
│   │   ├── home.html        # Home page
│   │   ├── inventory.html   # Inventory management
│   │   ├── layout.html      # Base layout template
│   │   ├── login.html       # Login form
│   │   ├── register.html    # User registration form
│   │   ├── reset_request.html # Password reset request
│   │   ├── reset_token.html # Password reset form
│   │   ├── sales.html       # Sales tracking page
│   │   ├── service_appointments.html # Service scheduling page
│   │   └── customer_service_data.html # Customer’s service data
│
├── users/                   # User-related functionality
│   ├── __init__.py          # User blueprint initialization
│   ├── forms.py             # Forms for user registration, login, and profile updates
│   ├── routes.py            # Routes for user-related operations
│   ├── utils.py             # Utility functions for email handling, password resets, etc.
│
├── __init__.py              # Application-level initialization
├── config.py                # Configuration settings (e.g., database URI, secret key)
├── db_models.py             # Database models (Users, Inventory, Sales, Service)
├── instance/
│   ├── site.db              # SQLite database file
├── app.py                   # Main entry point for the application
├── requirements.txt         # Python dependencies for the project
├── README.md                # Project documentation
```

---

## **Features**

### **Admin Features:**
- Manage inventory (add, edit, delete vehicles).
- View and track all sales records.
- Schedule and monitor service appointments.

### **Sales Staff Features:**
- Track sales records.
- View inventory details.

### **Service Staff Features:**
- Schedule and update service appointments.
- View customer service history.

### **Customer Features:**
- View and book service appointments.
- Manage account details.

---

## **Setup and Installation**

### **Prerequisites**
- Python 3.8 or higher installed on your system.
- `pip` package manager.

### **Clone the Repository**
```bash
git clone https://github.com/your-repo/unified-automotive.git
cd unified-automotive
```

### **Add config file inside flaskapp directory**
```bash
import os

class Config:
    SECRET_KEY = #os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db' #os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME =  #os.environ.get('EMAIL_USER')
    MAIL_PASSWORD =  #os.environ.get('EMAIL_PASS')  

```


### **Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## **Run the Application**

1. **Set Environment Variables** (For development mode):
   - On macOS/Linux:
     ```bash
     export FLASK_APP=app.py
     export FLASK_ENV=development
     ```
   - On Windows:
     ```bash
     set FLASK_APP=app.py
     set FLASK_ENV=development
     ```

2. **Run the Server**:
   ```bash
   flask run
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## **Database Initialization**
To set up the SQLite database:
1. Open a Python shell:
   ```bash
   flask shell
   ```
2. Initialize the database:
   ```python
   from db_models import db
   db.create_all()
   exit()
   ```

---

## **Folder Explanations**

### **`flaskapp/static/`**
- Contains static files like CSS, JavaScript, and images.
- **Profile Pictures:** Uploaded profile pictures are saved in `profile_pics`.

### **`flaskapp/templates/`**
- Contains Jinja2 HTML templates for rendering views.
- Base layout (`layout.html`) includes shared elements like headers and footers.

### **`users/`**
- Manages user authentication, registration, and profile updates.
- Includes email handling for password resets.

### **`db_models.py`**
- Contains database models:
  - `User`: Manages user details.
  - `Inventory`: Tracks vehicle inventory.
  - `Sales`: Records sales transactions.
  - `Service`: Handles service appointments.

---

## **Configuration**
### **`config.py`**
- Contains application settings:
  - **SECRET_KEY**: For securing forms and sessions.
  - **SQLALCHEMY_DATABASE_URI**: Database connection string.

---

## **Features in Development**
- Calendar view for service appointments.
- Enhanced analytics dashboards.
- Email/SMS notifications for reminders.

---

## **License**
This project is licensed under the MIT License.

---

## **Contributors**
- **Govardhan** - Developer  


---

With this documentation, new developers and users can quickly understand the application structure and functionality!