# Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant System
    participant Database

    User->>System: Login request
    System->>Database: Validate credentials
    Database-->>System: User data
    System-->>User: Login successful
```
