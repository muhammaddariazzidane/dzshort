# URL Shortener with Authentication

## Overview

This is a URL Shortener web application built with Flask and MongoDB. Users can create short URLs for long URLs, and only authenticated users can manage their own shortened URLs.

## Features

- **Shorten URLs**: Convert long URLs into short, easy-to-share links.
- **User Authentication**: Users can register and log in to manage their shortened URLs.
- **Access Control**: Only the owner of a URL can manage or delete it.
- **Statistics**: Track the number of times each short URL is accessed.

## Technologies Used

- **Backend**: Flask
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Token)

## Setup Instructions

### Prerequisites

- Python 3.x
- MongoDB instance (local or cloud)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/muhammaddariazzidane/dzshort-api.git

   cd dzshort-api
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv .venv

   # on Linux/Mac use
   source .venv/bin/activate

    # On Windows use
   .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root directory with the following content:

   ```env
   SECRET_KEY=your_secret_key
   MONGODB_URI=mongodb+srv://username:password@cluster_url/dbname
   JWT_SECRET_KEY=your_jwt_secret_key
   ```

5. **Run the application**:
   ```bash
   flask --app main run
   ```

The application should now be running on `http://127.0.0.1:5000/`.

## API Endpoints

### Authentication

- **Register**: `POST /register`

  ```json
  {
    "username": "your_username",
    "email": "your_email",
    "password": "your_password",
    "avatar": "optional_avatar_url"
  }
  ```

- **Login**: `POST /login`
  ```json
  {
    "email": "your_email",
    "password": "your_password"
  }
  ```

### URL Management

- **Create Short URL**: `POST /create-short-url`

  - Headers: `Authorization: Bearer <token>`

  ```json
  {
    "short_url": "http://example.com"
  }
  ```

- **Redirect to Original URL**: `GET /<short_url_id>`

### Response Example

- **Successful Registration**:

  ```json
  {
    "message": "User registered successfully",
    "user": {
      "_id": "unique_user_id",
      "username": "your_username",
      "email": "your_email",
      "avatar": "optional_avatar_url"
    }
  }
  ```

- **Successful Login**:

  ```json
  {
    "message": "Login successfully",
    "user": {
      "_id": "unique_user_id",
      "username": "your_username",
      "email": "your_email",
      "avatar": "optional_avatar_url"
    },
    "token": "your_jwt_token"
  }
  ```

- **Short URL Creation**:
  ```json
  {
    "short_url": "http://127.0.0.1:5000/short_url"
  }
  ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
