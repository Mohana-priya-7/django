# JWT Token Implementation Guide

## Overview
JWT (JSON Web Token) is a stateless authentication method that creates an encrypted token containing user information. This eliminates the need for server-side session storage and provides secure API access.

## What's Implemented

### 1. **Installation & Configuration** ✅

**Updated `requirements.txt`:**
```
Django>=4.2
djangorestframework>=3.14
psycopg2-binary
drf-spectacular
djangorestframework-simplejwt>=5.3.0
```

**Install packages:**
```bash
pip install -r requirements.txt
```

### 2. **Django Settings Configuration** ✅

**Updated `backend/settings.py`:**
- Added `rest_framework_simplejwt` to `INSTALLED_APPS`
- Configured JWT authentication as default
- Set token expiration times:
  - **Access Token**: 5 minutes (short-lived)
  - **Refresh Token**: 1 day (long-lived)

### 3. **User Authentication Endpoints** ✅

#### **Register** - `POST /register/`
Create a new user account
```json
Request:
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password2": "securepassword123"
}

Response (201):
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

#### **Login** - `POST /login/`
Get JWT tokens
```json
Request:
{
    "username": "john_doe",
    "password": "securepassword123"
}

Response (200):
{
    "message": "Login successful",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

#### **Refresh Token** - `POST /token/refresh/`
Get a new access token using refresh token
```json
Request:
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200):
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. **Protected API Endpoints** ✅

All product-related endpoints now require JWT authentication:
- `GET /products/` - List all products
- `POST /products/` - Create product
- `PUT /products/<id>/` - Update product
- `DELETE /products/<id>/` - Delete product
- `GET /total-sales/` - Get total sales
- `PUT /discount/<id>/` - Apply discount

**How to use protected endpoints:**

Add the access token to the request header:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Usage Examples

### Using cURL

#### 1. Register
```bash
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "test123",
    "password2": "test123"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "test123"
  }'
```

#### 3. Access Protected Endpoint
```bash
curl -X GET http://localhost:8000/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4. Refresh Token
```bash
curl -X POST http://localhost:8000/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
register_response = requests.post(
    f"{BASE_URL}/register/",
    json={
        "username": "john",
        "email": "john@example.com",
        "password": "test123",
        "password2": "test123"
    }
)

# Login
login_response = requests.post(
    f"{BASE_URL}/login/",
    json={
        "username": "john",
        "password": "test123"
    }
)

tokens = login_response.json()
access_token = tokens['access']

# Access Protected Endpoint
headers = {
    "Authorization": f"Bearer {access_token}"
}

products = requests.get(
    f"{BASE_URL}/products/",
    headers=headers
)

print(products.json())
```

### Using Postman

1. **Register**
   - Method: POST
   - URL: `http://localhost:8000/register/`
   - Body (JSON):
     ```json
     {
       "username": "john",
       "email": "john@example.com",
       "password": "test123",
       "password2": "test123"
     }
     ```

2. **Login**
   - Method: POST
   - URL: `http://localhost:8000/login/`
   - Body (JSON):
     ```json
     {
       "username": "john",
       "password": "test123"
     }
     ```
   - Copy the `access` token from response

3. **Access Product API**
   - Method: GET
   - URL: `http://localhost:8000/products/`
   - Headers:
     ```
     Authorization: Bearer YOUR_ACCESS_TOKEN
     ```

## How JWT Works

1. **User Registers** → Password is hashed and stored
2. **User Logs In** → Username/password verified, tokens generated
3. **Access Token** → Short-lived (5 min), used for API requests
4. **Refresh Token** → Long-lived (1 day), used to get new access token
5. **Each Request** → Client sends: `Authorization: Bearer {access_token}`
6. **Server Validates** → Token signature and expiration verified
7. **Token Expires** → Use refresh token to get new access token
8. **Refresh Expires** → User must login again

## How to Extend This

### Add Password Reset
```python
class PasswordReset(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        # Send reset email with token
        return Response({'message': 'Reset email sent'})
```

### Add OTP Verification
```python
class OTPVerify(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        # Verify OTP
        return Response({'message': 'OTP verified'})
```

### Add Change Password
```python
class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed'})
        return Response({'error': 'Old password incorrect'}, status=400)
```

## Token Structure

A JWT token consists of three parts separated by dots:
```
header.payload.signature
```

Example decoded token:
```json
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "token_type": "access",
  "exp": 1234567890,
  "iat": 1234567800,
  "jti": "abc123",
  "user_id": 1
}

Signature:
HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), SECRET_KEY)
```

## Security Best Practices

1. **Never expose tokens** - Don't log or send tokens in plain text
2. **Use HTTPS only** - Tokens must be transmitted over secure connections
3. **Store securely** - In client apps, use secure storage (httpOnly cookies, encrypted storage)
4. **Short expiration** - Access tokens should expire quickly (5-15 minutes)
5. **Rotate secrets** - Change SECRET_KEY periodically
6. **Validate signatures** - Always verify token signatures server-side
7. **Use refresh tokens** - Keep access tokens short-lived

## Database Migrations

If you haven't already, run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing the Implementation

Run the development server:
```bash
python manage.py runserver
```

Then visit the Swagger UI:
```
http://localhost:8000/swagger/
```

All endpoints are documented and you can test them directly from the browser!

## Common Issues & Solutions

**Issue: Token expired**
- Solution: Use refresh endpoint to get new access token

**Issue: 401 Unauthorized on protected endpoints**
- Solution: Make sure to include `Authorization: Bearer {token}` header

**Issue: Invalid token signature**
- Solution: Ensure you're using the correct token from login response

**Issue: Permission denied**
- Solution: User must be authenticated (use login endpoint first)

## File Structure

```
products/
├── models.py (Product model)
├── serializers.py (UserSerializer, LoginSerializer, ProductSerializer)
├── views.py (Register, Login, RefreshTokenView, + protected product views)
├── urls.py (All endpoint routes)

backend/
├── settings.py (JWT configuration, INSTALLED_APPS)
└── urls.py (Main URL configuration)
```

## Next Steps

1. ✅ Install packages: `pip install -r requirements.txt`
2. ✅ Run migrations: `python manage.py migrate`
3. ✅ Test registration: POST `/register/`
4. ✅ Test login: POST `/login/`
5. ✅ Test protected APIs: Use access token
6. ⏳ Implement additional features (password reset, OTP, etc.)
