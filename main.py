from database import Database
from login_ui import LoginUI
from dashboard import Dashboard

def main():
    try:
        # Initialize database
        db = Database()
        
        # Start with login
        login_window = LoginUI(db)
        user_id = login_window.run()
        
        # If login successful, show dashboard
        if user_id:
            print(f"Successfully logged in with user_id: {user_id}")  # Debug print
            dashboard = Dashboard(user_id, db)
            dashboard.run()
    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Debug print

if __name__ == "__main__":
    main()
