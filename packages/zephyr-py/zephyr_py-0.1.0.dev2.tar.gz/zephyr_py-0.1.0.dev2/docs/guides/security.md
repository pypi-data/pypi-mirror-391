# Security Guide

This guide covers security features in the Zephyr Framework.

## Security Architecture

```mermaid
graph TD
    A[Security Layer] --> B[Authentication]
    A --> C[Authorization]
    A --> D[CSRF Protection]
    A --> E[Rate Limiting]
    B --> F[JWT]
    B --> G[OAuth2]
    B --> H[Session]
    C --> I[RBAC]
    C --> J[Permissions]
    C --> K[Policies]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D,E fill:#bbf,stroke:#333,stroke-width:2px
    style F,G,H,I,J,K fill:#dfd,stroke:#333,stroke-width:2px
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth Middleware
    participant J as JWT Service
    participant D as Database
    
    C->>A: Request + Credentials
    A->>D: Validate Credentials
    D-->>A: User Data
    A->>J: Generate Token
    J-->>A: JWT Token
    A-->>C: Token Response
```

## JWT Implementation

```python
from zephyr.security import JWT, JWTConfig

jwt = JWT(JWTConfig(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expire=30,  # minutes
    refresh_token_expire=7,  # days
))

@app.route("/login", methods=["POST"])
async def login(credentials: LoginCredentials):
    user = await authenticate_user(credentials)
    tokens = await jwt.create_tokens(user.id)
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token
    }
```

## Role-Based Access Control

```mermaid
graph TD
    A[User] --> B[Roles]
    B --> C[Permissions]
    C --> D[Resources]
    B --> E[Admin Role]
    B --> F[User Role]
    B --> G[Guest Role]
    E --> H[Full Access]
    F --> I[Limited Access]
    G --> J[Read Only]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C,D fill:#dfd,stroke:#333,stroke-width:2px
    style E,F,G fill:#fdd,stroke:#333,stroke-width:2px
    style H,I,J fill:#dff,stroke:#333,stroke-width:2px
```

## CSRF Protection

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant T as Token Store
    
    C->>S: GET Request
    S->>T: Generate Token
    T-->>S: CSRF Token
    S-->>C: Response + Token
    C->>S: POST Request + Token
    S->>T: Validate Token
    T-->>S: Valid/Invalid
    S-->>C: Response
```

## Rate Limiting

```mermaid
graph LR
    A[Request] --> B{Rate Limiter}
    B -->|Under Limit| C[Handler]
    B -->|Over Limit| D[429 Error]
    B --> E[Store]
    E --> F[Memory]
    E --> G[Redis]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C,D fill:#dfd,stroke:#333,stroke-width:2px
    style E fill:#fdd,stroke:#333,stroke-width:2px
    style F,G fill:#dff,stroke:#333,stroke-width:2px
```

## Security Headers

```python
from zephyr.security import SecurityHeaders

app.use_middleware(SecurityHeaders, {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
})
```

## OAuth2 Integration

```mermaid
sequenceDiagram
    participant U as User
    participant A as App
    participant O as OAuth Provider
    participant D as Database
    
    U->>A: Login with OAuth
    A->>O: Redirect to Provider
    O->>U: Auth Prompt
    U->>O: Approve
    O->>A: Auth Code
    A->>O: Exchange Code
    O->>A: Access Token
    A->>O: Get User Info
    O->>A: User Data
    A->>D: Create/Update User
    A->>U: Login Success
```

## Password Security

```mermaid
graph TD
    A[Password] --> B[Hash Function]
    B --> C[Salt]
    B --> D[Pepper]
    B --> E[Iterations]
    C --> F[Hashed Password]
    D --> F
    E --> F
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C,D,E fill:#dfd,stroke:#333,stroke-width:2px
    style F fill:#fdd,stroke:#333,stroke-width:2px
```

Example implementation:

```python
from zephyr.security import PasswordHasher

hasher = PasswordHasher()

# Hash password
hashed = await hasher.hash("user_password")

# Verify password
is_valid = await hasher.verify("user_password", hashed)
```

## Security Best Practices

1. **Authentication**:
   ```mermaid
   graph TD
       A[Authentication] --> B[Strong Passwords]
       A --> C[MFA Support]
       A --> D[Session Management]
       A --> E[Account Recovery]
       style A fill:#f9f,stroke:#333,stroke-width:2px
       style B,C,D,E fill:#bbf,stroke:#333,stroke-width:2px
   ```

2. **Data Protection**:
   ```mermaid
   graph TD
       A[Data Protection] --> B[Encryption at Rest]
       A --> C[TLS in Transit]
       A --> D[Key Management]
       A --> E[Data Masking]
       style A fill:#f9f,stroke:#333,stroke-width:2px
       style B,C,D,E fill:#bbf,stroke:#333,stroke-width:2px
   ```

3. **Access Control**:
   ```mermaid
   graph TD
       A[Access Control] --> B[Principle of Least Privilege]
       A --> C[Role-Based Access]
       A --> D[Resource-Based Access]
       A --> E[API Security]
       style A fill:#f9f,stroke:#333,stroke-width:2px
       style B,C,D,E fill:#bbf,stroke:#333,stroke-width:2px
   ```
