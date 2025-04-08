# Django Project

This repository contains a Django-based web application developed by Kratik Gupta. The project is structured to include multiple apps and functionalities, providing a comprehensive example of a Django project setup.

## Project Structure

The project includes the following main directories and files:

- **DJANGO_PROJECT/**: The main Django project directory containing settings and configurations.
- **accounts/**: Handles user authentication and related functionalities.
- **media/**: Directory for user-uploaded media files.
- **model/**: Contains the data models used in the project.
- **profile_app/**: Manages user profiles and related features.
- **social_media/**: Implements social media-related functionalities.
- **static/**: Holds static files such as CSS, JavaScript, and images.
- **templates/**: Contains HTML templates for rendering views.
- **venv/**: Virtual environment for managing project dependencies.
- **db.sqlite3**: SQLite database file used for development.
- **manage.py**: Command-line utility for interacting with the Django project.
- **requirements.txt**: Lists the Python packages required to run the project.

## Getting Started

To set up and run this project locally, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/kratikgupta77/django_project.git
   ```


2. **Navigate to the project directory**:

   ```bash
   cd django_project
   ```


3. **Set up a virtual environment** (if not already set up):

   ```bash
   python3 -m venv venv
   ```


4. **Activate the virtual environment**:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

5. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```


6. **Apply migrations to set up the database**:

   ```bash
   python manage.py migrate
   ```


7. **Run the development server**:

   ```bash
   python manage.py runserver
   ```


8. **Access the application**:

   Open your web browser and navigate to `http://127.0.0.1:8000/` to view the application.

## Notes

- Ensure that you have Python and pip installed on your system before proceeding with the setup.
- It's recommended to use the virtual environment provided (`venv/`) to manage dependencies.
- For any issues or contributions, please refer to the repository's issue tracker.

---

*This README was generated based on the project structure and available information in the repository.* 
