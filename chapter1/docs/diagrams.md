# Chapter 1: Diagrams

## Entity-Relationship diagram for this chapter's schema

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : included_in
    ORDERS ||--o| PAYMENTS : has

    USERS {
        int id PK
        text email UK
        text full_name
        timestamptz created_at
    }
    ORDERS {
        int id PK
        int user_id FK
        text status
        timestamptz created_at
    }
    PRODUCTS {
        int id PK
        text sku UK
        text name
        numeric price
        int stock_qty
    }
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        numeric unit_price
    }
    PAYMENTS {
        int id PK
        int order_id FK
        numeric amount
        text method
        text status
        timestamptz paid_at
    }
```

## Relationship cardinality cheat sheet

```mermaid
graph LR
    A["One USER"] -->|"1 : many"| B["Many ORDERS"]
    C["One ORDER"] -->|"1 : many"| D["Many ORDER_ITEMS"]
    E["One PRODUCT"] -->|"1 : many"| D
    F["One ORDER"] -->|"1 : 0-or-1"| G["One PAYMENT"]
```

- `||--o{` = "exactly one" on the left, "zero or many" on the right
- `||--|{` = "exactly one" on the left, "one or many" on the right
- `||--o|` = "exactly one" on the left, "zero or one" on the right
