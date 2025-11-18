# Zephyr Framework Documentation

Welcome to the Zephyr Framework documentation! This comprehensive guide will help you understand and use the framework effectively.

## Framework Overview

![Architecture Overview](assets/diagrams/architecture.png)

Zephyr is a modern, high-performance Python web framework designed for building scalable applications. It combines the best features of FastAPI, Django, and other modern frameworks while adding enterprise-grade capabilities.

### Key Features

```mermaid
mindmap
  root((Zephyr))
    Core Features
      Fast ASGI Server
      Type Safety
      Auto Documentation
      GraphQL Support
    Security
      JWT Auth
      RBAC
      CSRF Protection
      Rate Limiting
    Data Layer
      ORM
      Migrations
      Query Builder
      Caching
    Real-time
      WebSockets
      Server Events
      Pub/Sub
    Development
      Hot Reload
      Debug Tools
      Testing Suite
      CLI Tools
```

## Request Lifecycle

![Request Lifecycle](assets/diagrams/request_lifecycle.png)

Understanding how Zephyr handles requests is crucial for building efficient applications.

## Component Architecture

```mermaid
graph LR
    A[Application] --> B[Router]
    A --> C[Middleware]
    A --> D[Services]
    B --> E[Controllers]
    B --> F[WebSocket]
    B --> G[GraphQL]
    D --> H[Database]
    D --> I[Cache]
    D --> J[Queue]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F,G fill:#dfd,stroke:#333,stroke-width:2px
    style H,I,J fill:#ddd,stroke:#333,stroke-width:2px
```

## Quick Navigation

- [Getting Started](guides/getting_started.md)
- [Core Concepts](guides/core_concepts.md)
- [Security](guides/security.md)
- [Database](guides/database.md)
- [WebSockets](guides/websockets.md)
- [GraphQL](guides/graphql.md)
- [Testing](guides/testing.md)
- [Deployment](guides/deployment.md)
