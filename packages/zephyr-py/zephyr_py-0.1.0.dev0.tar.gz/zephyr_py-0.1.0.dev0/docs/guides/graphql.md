# GraphQL Guide

This guide covers GraphQL implementation in the Zephyr Framework.

## GraphQL Architecture

```mermaid
graph TD
    A[GraphQL Server] --> B[Schema]
    A --> C[Resolvers]
    A --> D[DataLoaders]
    B --> E[Types]
    B --> F[Queries]
    B --> G[Mutations]
    B --> H[Subscriptions]
    C --> I[Query Resolvers]
    C --> J[Mutation Resolvers]
    C --> K[Subscription Resolvers]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F,G,H fill:#dfd,stroke:#333,stroke-width:2px
    style I,J,K fill:#fdd,stroke:#333,stroke-width:2px
```

## Schema Definition

```python
from zephyr.graphql import Schema, ObjectType, Field

class User(ObjectType):
    id: int = Field()
    username: str = Field()
    email: str = Field()
    posts: List["Post"] = Field()

class Post(ObjectType):
    id: int = Field()
    title: str = Field()
    content: str = Field()
    author: User = Field()

class Query(ObjectType):
    user = Field(User, id=int)
    posts = Field(List[Post])

    async def resolve_user(self, id: int):
        return await User.get(id)

    async def resolve_posts(self):
        return await Post.all()

schema = Schema(query=Query)
```

## Query Resolution Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant R as Resolver
    participant D as DataLoader
    participant DB as Database
    
    C->>S: GraphQL Query
    S->>R: Execute Resolver
    R->>D: Batch Load
    D->>DB: Single Query
    DB-->>D: Data
    D-->>R: Results
    R-->>S: Resolved Data
    S-->>C: Response
```

## DataLoader Implementation

```mermaid
graph LR
    A[DataLoader] --> B[Batch Function]
    B --> C[Cache]
    B --> D[Database]
    C --> E[Results]
    D --> E
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C,D fill:#dfd,stroke:#333,stroke-width:2px
    style E fill:#fdd,stroke:#333,stroke-width:2px
```

Example implementation:

```python
from zephyr.graphql import DataLoader

class UserLoader(DataLoader):
    async def batch_load(self, ids: List[int]) -> List[User]:
        users = await User.filter(id__in=ids)
        return [users.get(id) for id in ids]

user_loader = UserLoader()

class Post(ObjectType):
    author = Field(User)
    
    async def resolve_author(self, info):
        return await user_loader.load(self.author_id)
```

## Mutations

```mermaid
graph TD
    A[Mutation] --> B[Input Type]
    A --> C[Resolver]
    C --> D[Validation]
    C --> E[Database]
    C --> F[Response Type]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C fill:#bbf,stroke:#333,stroke-width:2px
    style D,E,F fill:#dfd,stroke:#333,stroke-width:2px
```

Example:

```python
class CreateUserInput(InputType):
    username: str = Field()
    email: str = Field()
    password: str = Field()

class Mutation(ObjectType):
    create_user = Field(
        User,
        input=CreateUserInput
    )
    
    async def resolve_create_user(
        self,
        input: CreateUserInput
    ) -> User:
        return await User.create(**input.dict())

schema = Schema(
    query=Query,
    mutation=Mutation
)
```

## Subscriptions

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant P as PubSub
    participant R as Resolver
    
    C->>S: Subscribe
    S->>R: Setup Subscription
    R->>P: Subscribe to Events
    
    loop Event Publishing
        P->>R: New Event
        R->>S: Resolve Event
        S-->>C: Send Update
    end
    
    C->>S: Unsubscribe
    S->>P: Cleanup
```

Implementation:

```python
from zephyr.graphql import Subscription, PubSub

pubsub = PubSub()

class Subscription(ObjectType):
    user_created = Field(User)
    
    async def subscribe_user_created(self, info):
        return await pubsub.subscribe("USER_CREATED")
        
    async def resolve_user_created(self, info, user: User):
        return user

# In mutation
async def resolve_create_user(self, input):
    user = await User.create(**input.dict())
    await pubsub.publish("USER_CREATED", user)
    return user
```

## Error Handling

```mermaid
graph TD
    A[GraphQL Error] --> B[Validation Error]
    A --> C[Resolver Error]
    A --> D[Schema Error]
    B --> E[Input Validation]
    C --> F[Business Logic]
    D --> G[Type Checking]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F,G fill:#dfd,stroke:#333,stroke-width:2px
```

## Performance Optimization

```mermaid
graph LR
    A[Optimization] --> B[DataLoader]
    A --> C[Field Selection]
    A --> D[Caching]
    B --> E[Batch Loading]
    C --> F[Query Cost]
    D --> G[Result Cache]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B,C,D fill:#bbf,stroke:#333,stroke-width:2px
    style E,F,G fill:#dfd,stroke:#333,stroke-width:2px
```

## Client Usage

```typescript
// Using GraphQL Client
const client = new GraphQLClient('http://localhost:8000/graphql');

// Query
const { user } = await client.query(`
    query GetUser($id: Int!) {
        user(id: $id) {
            id
            username
            posts {
                id
                title
            }
        }
    }
`, { id: 1 });

// Mutation
const { createUser } = await client.mutate(`
    mutation CreateUser($input: CreateUserInput!) {
        createUser(input: $input) {
            id
            username
        }
    }
`, {
    input: {
        username: "john",
        email: "john@example.com"
    }
});

// Subscription
const subscription = client.subscribe(`
    subscription OnUserCreated {
        userCreated {
            id
            username
        }
    }
`);

subscription.subscribe({
    next: ({ userCreated }) => {
        console.log('New user:', userCreated);
    }
});
```
