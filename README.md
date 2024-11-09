# Forum Application

This is a forum application built with FastAPI. It allows users to register, login, create topics, and reply to messages. The application also includes categories for organizing topics.

## Features

- User registration and authentication
- Create and manage topics
- Reply to messages
- Organize topics into categories
- User profile pages

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/forum-app.git
    cd forum-app
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the application:
    ```sh
    uvicorn main:app --reload
    ```

## Usage

- Access the application at `http://127.0.0.1:8000`.
- Register a new user or login with an existing account.
- Navigate through categories, create topics, and reply to messages.

## Project Structure

- `main.py`: The main entry point of the application.
- `routers/`: Contains the API and web routers for different functionalities.
- `templates/`: Contains the HTML templates for rendering web pages.
- `static/css/`: Contains the CSS files for styling the web pages.
- `common/`: Contains common utilities and configurations.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License.