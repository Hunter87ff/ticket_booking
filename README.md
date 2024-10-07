## Overview
This project is a ticket booking application built using Flask, MongoDB, and other technologies. The application includes various components such as API endpoints, error handling, and user authentication.

## Key Components

### 1. app.py
- **Purpose**: Main application file that initializes the Flask app and defines routes.
- **Key Sections**:
    - **Error Handlers**: Custom error pages for 404, 401, 500, and 405 errors.
    - **Routes**: 
        - `/`: Renders the home page.
        - `/validate`: Renders the validation page.
        - `/generate`: Renders the ticket generation page (requires manager authentication).
        - `/dashboard`: Renders the admin dashboard (requires manager authentication).

### 2. api.py
- **Purpose**: Defines API endpoints for ticket generation, ticket validation, date updates, and user login.
- **Key Sections**:
    - **Endpoints**:
        - `/api/gen`: Generates a new ticket (requires manager authentication).
        - `/ticket/<token>`: Validates and displays a ticket.
        - `/api/update_date`: Updates the event date (requires manager authentication).
        - `/login`: Handles user login and redirects to the dashboard if successful.

### 3. config.py
- **Purpose**: Configuration file that sets up the database connections, environment variables, and utility functions.
- **Key Sections**:
    - **Database Setup**: Connects to MongoDB and initializes collections.
    - **Utility Functions**: Functions for logging, ticket management, and user authentication.
    - **Classes**:
        - `Ticket`: Manages ticket creation and storage.
        - `Event`: Manages event details and ticket tracking.
        - `Admin`: Manages admin user details and authentication.


## Setup Instructions

To set up the application on your local machine, follow these steps:

### Prerequisites

Ensure you have the following installed:
- Python 3.x
- pip (Python package installer)
- MongoDB

### Steps

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/ticket_booking.git
    cd ticket_booking
    ```

2. **Create a Virtual Environment**:
    ```sh
    python -m venv venv
    ```

3. **Activate the Virtual Environment**:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

4. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

5. **Set Up Environment Variables**:
    Create a `.env` file in the root directory and add the following variables:
    ```env
    MONGO_URI=mongo_uri
    DEV_ENV=True
    ```

6. **Run the Application**:
    ```sh
    python app.py
    ```

7. **Access the Application**:
    Open your web browser and navigate to `http://127.0.0.1:8787`.
