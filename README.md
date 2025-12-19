# Test Case & Defect Tracker (Flask)

A secure, role-based web application for managing **Projects**, **Test Cases**, and **Defects** in a centralised database.  
Built to reflect a QA workflow in a mobile banking context (tester ↔ developer ↔ admin).

---
## Features

- User authentication (register/login/logout)
- Role-based access control (Admin / Developer / Tester)
- CRUD for:
  - Projects
  - Test cases (linked to projects)
  - Defects (linked to projects and optionally linked to a test case)
- Validation + user feedback (flash messages)
- Automated unit tests with `pytest`

---

## Tech Stack

- Python (Flask)
- SQLite (shared database file)
- SQLAlchemy ORM
- Flask-Login
- Pytest

---

# First-time setup (creates tables)
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"

---

## Roles & Permissions (summary)

- **Admin**
  - Full access
  - Can delete projects (and other restricted actions depending on your config)
- **Tester**
  - Create and manage projects, test cases, defects
  - Some destructive actions may be limited depending on ownership rules
- **Developer**
  - View projects/test cases/defects
  - Update defect workflow/status (as implemented)

  ## Demo Accounts (dummy)

These accounts are **for marking/demo purposes only** (do not use real passwords).

### Admin
- Jane Doe  
  Email: `JaneDoe123@gmail.com`  
  Password: `ILovemyCat`

### Developers
- Cliff Roger  
  Email: `Cliffton670@gmail.com`  
  Password: `aRsenal75?`

- Karim Den  
  Email: `Karimden@gmail.com`  
  Password: `denytist112`

### Testers
- Daniel Isaac  
  Email: `Danielis@gmail.com`  
  Password: `junnysunny21`

- Ria Bains  
  Email: `riabains16@gmail.com`  
  Password: `Lolaio90`

If these accounts don’t work on a fresh install:
1) Run the app  
2) Use the **Register** page to recreate them (choose the correct role)

---

## Project Setup (Local)

### 1) Clone the repo
```bash
git clone https://github.com/<your-username>/testcaseweb.git
cd testcaseweb
