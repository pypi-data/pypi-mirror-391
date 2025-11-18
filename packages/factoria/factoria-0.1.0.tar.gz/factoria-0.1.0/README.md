# Factoria

**Factoria** is a lightweight Python library for generating one or more [Pydantic](https://docs.pydantic.dev/) model instances with **chainable state modifiers**.  
It’s especially useful for testing, seeding, or creating predictable data scenarios.

## Features

- Generate single or multiple Pydantic models easily  
- Apply state transformations fluently
- Simple base class for building factories  
- Perfect for unit testing and data seeding  

## Installation

Using [Poetry](https://python-poetry.org/):

```bash
poetry add factoria
```

Or with pip

```bash
pip install factoria
```

## Examples

Create a Factory

```python
from pydantic import BaseModel
from factoria import BaseFactory


class User(BaseModel):
    id: int
    name: str
    email: str


class UserFactory(BaseFactory):
    def definition(self):
        return User(
            id=1,
            name="Alice",
            email="alice@example.com",
        )
```

Generate One or Many

```python
# Create one instance
user = UserFactory().make()
print(user)
# → User(id=1, name='Alice', email='alice@example.com')

# Create multiple instances
users = UserFactory().count(3).make()
print(len(users))
# → 3
```

You can define chainable states using the @apply decorator

```python
from datetime import datetime, timedelta
from pydantic import BaseModel
from factoria import BaseFactory, apply


class Order(BaseModel):
    id: int
    customer: str
    total: float
    status: str = "pending"
    paid_at: datetime | None = None
    shipped_at: datetime | None = None
    cancelled: bool = False


class OrderFactory(BaseFactory):

    def definition(self):
        return Order(
            id=1,
            customer="John Doe",
            total=199.90,
        )

    @apply
    def paid(self, obj):
        obj.status = "paid"
        obj.paid_at = datetime.utcnow()

    @apply
    def shipped(self, obj):
        obj.status = "shipped"
        obj.shipped_at = datetime.utcnow() + timedelta(days=1)

    @apply
    def cancelled(self, obj):
        obj.status = "cancelled"
        obj.cancelled = True
```

Some modifiers examples

```python
# One paid order
paid_order = OrderFactory().paid().make()

# Two shipped orders
shipped_orders = OrderFactory().count(2).shipped().make()

# Three cancelled orders
cancelled_orders = OrderFactory().count(3).cancelled().make()

# A complex example (paid and shipped)
paid_and_shipped = OrderFactory().count(2).paid().shipped().make()
```