# clue-subscriptions-mgt-api

## Setup Instructions

### Using Virtual Environments

1. Clone the repo: `git clone https://github.com/TeeblaQ1/clue-subscriptions-mgt-api.git`
2. Create venv: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install requirements: `pip install -r requirements.txt`
5. Create env file: copy .env.example into .env and fill the values
6. Run: `python run.py`
7. Create admin user (see Admin User Setup below)

### Using Docker
1. Clone the repo: `git clone https://github.com/TeeblaQ1/clue-subscriptions-mgt-api.git`
2. Create env file: copy .env.example into .env and fill the values
3. Build and run: `docker compose up -d --build`
4. Create admin user (see Admin User Setup below)
5. Run Test 

## Tests
1. Using virtual environments (activate the virtual environment) and run the command below
    `pytest tests`
2. Using docker (exec into the container) and run the command below
    `docker compose exec api pytest tests`
    
## DB
If the DATABASE_URL is not set in the env file, it defaults to a SQLIite db

## Admin User Setup

To access admin-only endpoints (like creating subscription plans), you need to create an admin user. The API includes a CLI command for this purpose.

### Using Virtual Environment

1. **Activate your virtual environment**:
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Set the FLASK_APP environment variable**:
   ```bash
   export FLASK_APP=run.py  # Linux/Mac
   # or
   set FLASK_APP=run.py     # Windows
   ```

3. **Create admin user using the CLI command**:
   ```bash
   flask create-admin admin@example.com your_password_here
   ```

### Using Docker

1. **Exec into the running container**:
   ```bash
   docker exec -it <container_name> bash
   ```

2. **Create admin user**:
   ```bash
   flask create-admin admin@example.com your_password_here
   ```

### Example

```bash
# Create an admin user with email admin@company.com and password admin123
flask create-admin admin@company.com admin123
```

**Success Response**:
```
Admin user admin@company.com created successfully.
```

**Error Response** (if user already exists):
```
User with email admin@company.com already exists.
```

### Important Notes

- Admin users can access all endpoints including admin-only ones
- Admin users can create, modify, and view all subscription plans
- Admin users can view all active subscriptions across all users
- Regular users can only manage their own subscriptions
- The admin user creation command is only available during development/setup

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Endpoints

#### Authentication Endpoints

##### 1. User Registration
- **URL**: `/api/register`
- **Method**: `POST`
- **Authentication**: Not required
- **Description**: Create a new user account

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (201):
```json
{
  "message": "User created successfully",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 1
  },
  "status_code": 201
}
```

**Validation Rules**:
- Email must be valid format
- Password must be at least 8 characters

---

##### 2. User Login
- **URL**: `/api/login`
- **Method**: `POST`
- **Authentication**: Not required
- **Description**: Authenticate user and get JWT token

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200):
```json
{
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 1
  },
  "status_code": 200
}
```

---

#### Subscription Plan Endpoints

##### 3. Create Subscription Plan
- **URL**: `/api/subscriptions/plans`
- **Method**: `POST`
- **Authentication**: Admin required
- **Description**: Create a new subscription plan

**Request Body**:
```json
{
  "name": "Premium Plan",
  "description": "Access to all premium features",
  "price_cents": 2999
}
```

**Response** (201):
```json
{
  "message": "Plan created successfully",
  "data": {
    "id": 1,
    "name": "Premium Plan",
    "description": "Access to all premium features",
    "price_cents": 2999,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "status_code": 201
}
```

**Validation Rules**:
- Name is required and must be at least 1 character
- Description is optional but must be at least 1 character if provided
- Price must be in cents and non-negative

---

##### 4. List Subscription Plans
- **URL**: `/api/subscriptions/plans`
- **Method**: `GET`
- **Authentication**: Not required
- **Description**: Get all available subscription plans

**Response** (200):
```json
{
  "message": "Plans fetched successfully",
  "data": [
    {
      "id": 1,
      "name": "Basic Plan",
      "description": "Basic features access",
      "price_cents": 999,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    },
    {
      "id": 2,
      "name": "Premium Plan",
      "description": "Access to all premium features",
      "price_cents": 2999,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "status_code": 200
}
```

---

#### Subscription Management Endpoints

##### 5. Subscribe to Plan
- **URL**: `/api/subscriptions/subscribe`
- **Method**: `POST`
- **Authentication**: JWT required
- **Description**: Subscribe to a subscription plan

**Request Body**:
```json
{
  "plan_id": 1,
  "duration_days": 30
}
```

**Response** (200):
```json
{
  "message": "Subscription created successfully",
  "data": {
    "id": 1,
    "user_id": 1,
    "plan_id": 1,
    "starts_at": "2024-01-01T00:00:00",
    "ends_at": "2024-01-31T00:00:00",
    "status": "active",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "status_code": 200
}
```

**Validation Rules**:
- Plan ID must be a positive integer
- Duration must be at least 1 day

**Note**: This endpoint automatically cancels any existing active subscription before creating a new one.

---

##### 6. Change Subscription Plan
- **URL**: `/api/subscriptions/change-plan`
- **Method**: `POST`
- **Authentication**: JWT required
- **Description**: Change the plan of an active subscription

**Request Body**:
```json
{
  "plan_id": 2
}
```

**Response** (200):
```json
{
  "message": "Subscription plan changed successfully",
  "data": {
    "id": 1,
    "user_id": 1,
    "plan_id": 2,
    "starts_at": "2024-01-01T00:00:00",
    "ends_at": "2024-01-31T00:00:00",
    "status": "active",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "status_code": 200
}
```

**Requirements**:
- User must have an active subscription
- Plan ID must exist

---

##### 7. Cancel Subscription
- **URL**: `/api/subscriptions/cancel`
- **Method**: `POST`
- **Authentication**: JWT required
- **Description**: Cancel the user's active subscription

**Request Body**: None required

**Response** (200):
```json
{
  "message": "Subscription cancelled successfully",
  "status_code": 200
}
```

---

##### 8. Get Active Subscription
- **URL**: `/api/subscriptions/active`
- **Method**: `GET`
- **Authentication**: JWT required
- **Description**: Get the user's current active subscription

**Response** (200):
```json
{
  "message": "Active subscription fetched successfully",
  "data": {
    "id": 1,
    "name": "Premium Plan",
    "description": "Access to all premium features",
    "plan_id": 2,
    "starts_at": "2024-01-01T00:00:00",
    "ends_at": "2024-01-31T00:00:00",
    "status": "active"
  },
  "status_code": 200
}
```

**Response** (200) - No active subscription:
```json
{
  "message": "Active subscription fetched successfully",
  "data": null,
  "status_code": 200
}
```

---

##### 9. Get All Active Subscriptions (Admin)
- **URL**: `/api/subscriptions/active/all`
- **Method**: `GET`
- **Authentication**: Admin required
- **Description**: Get all active subscriptions (optionally filtered by user IDs)

**Query Parameters**:
- `user_ids` (optional): Comma-separated list of user IDs to filter by

**Example**: `/api/subscriptions/active/all?user_ids=1,2,3`

**Response** (200):
```json
{
  "message": "All active subscriptions fetched successfully",
  "data": [
    {
      "user_id": 1,
      "id": 1,
      "name": "Premium Plan",
      "description": "Access to all premium features",
      "plan_id": 2,
      "starts_at": "2024-01-01T00:00:00",
      "ends_at": "2024-01-31T00:00:00",
      "status": "active"
    },
    {
      "user_id": 2,
      "id": 2,
      "name": "Basic Plan",
      "description": "Basic features access",
      "plan_id": 1,
      "starts_at": "2024-01-01T00:00:00",
      "ends_at": "2024-01-31T00:00:00",
      "status": "active"
    }
  ],
  "status_code": 200
}
```

---

##### 10. Get Subscription History
- **URL**: `/api/subscriptions/history`
- **Method**: `GET`
- **Authentication**: JWT required
- **Description**: Get paginated subscription history for the authenticated user

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 10)

**Example**: `/api/subscriptions/history?page=1&page_size=5`

**Response** (200):
```json
{
  "message": "Subscription history fetched successfully",
  "data": [
    {
      "id": 1,
      "name": "Premium Plan",
      "description": "Access to all premium features",
      "plan_id": 2,
      "starts_at": "2024-01-01T00:00:00",
      "ends_at": "2024-01-31T00:00:00",
      "status": "cancelled"
    },
    {
      "id": 2,
      "name": "Basic Plan",
      "description": "Basic features access",
      "plan_id": 1,
      "starts_at": "2023-12-01T00:00:00",
      "ends_at": "2023-12-31T00:00:00",
      "status": "expired"
    }
  ],
  "status_code": 200
}
```

---

### Testing the API

#### Using cURL

##### 1. Register a new user:
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

##### 2. Login:
```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

##### 3. Subscribe to a plan (replace TOKEN with actual token):
```bash
curl -X POST http://localhost:8000/api/subscriptions/subscribe \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "plan_id": 1,
    "duration_days": 30
  }'
```

##### 4. Get active subscription:
```bash
curl -X GET http://localhost:8000/api/subscriptions/active \
  -H "Authorization: Bearer TOKEN"
```

#### Using Postman

1. **Import the collection**: Create a new collection in Postman
2. **Set base URL**: `http://localhost:8000`
3. **Create environment variables**:
   - `base_url`: `http://localhost:8000`
   - `token`: (will be set after login)
4. **Set up requests**:
   - Register: `POST {{base_url}}/api/register`
   - Login: `POST {{base_url}}/api/login`
   - Subscribe: `POST {{base_url}}/api/subscriptions/subscribe`
   - Get Active: `GET {{base_url}}/api/subscriptions/active`

#### Using Python requests

```python
import requests

base_url = "http://localhost:8000"

# Register
response = requests.post(f"{base_url}/api/register", json={
    "email": "test@example.com",
    "password": "password123"
})
print(response.json())

# Login
response = requests.post(f"{base_url}/api/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = response.json()["data"]["token"]

# Subscribe
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{base_url}/api/subscriptions/subscribe", 
                        json={"plan_id": 1, "duration_days": 30},
                        headers=headers)
print(response.json())
```

### Error Responses

All endpoints return consistent error responses:

**Validation Error** (400):
```json
{
  "message": "Invalid input",
  "error": {
    "email": ["Not a valid email address."],
    "password": ["String must be at least 8 characters long."]
  },
  "status_code": 400
}
```

**Authentication Error** (401):
```json
{
  "message": "Invalid credentials",
  "status_code": 401
}
```

**Not Found Error** (404):
```json
{
  "message": "Plan not found",
  "status_code": 404
}
```

**Unauthorized Error** (403):
```json
{
  "message": "Admin access required",
  "status_code": 403
}
```

### Notes

- All timestamps are in ISO 8601 format
- Prices are stored in cents to avoid floating-point precision issues
- The API automatically handles subscription conflicts by cancelling existing active subscriptions
- Admin endpoints require special privileges
- JWT tokens should be included in the Authorization header for protected endpoints
