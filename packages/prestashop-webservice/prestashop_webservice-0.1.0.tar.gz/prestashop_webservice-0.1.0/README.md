# PrestaShop Webservice

Python client to interact with PrestaShop API in a simple and efficient way. Designed for internal company use.

## Features

- 🚀 Optimized HTTP client with persistent connections
- 💾 Automatic response caching with configurable TTL
- 🔒 Singleton pattern for efficient connection management
- 📝 Integrated logging with Loguru
- 🎯 Full type hints support
- 🔄 Simple and reusable primitive queries
- 📦 Type-safe parameter system

## Installation

### Direct installation from repository

```bash
pip install git+https://github.com/yourcompany/prestashop-webservice.git
```

### Development mode installation

```bash
git clone https://github.com/yourcompany/prestashop-webservice.git
cd prestashop-webservice
pip install -e .
```

### Installation with development dependencies

```bash
pip install -e ".[dev]"
```

## Usage

### Initialization

```python
from prestashop_webservice import Client

# Create repository instance (Singleton)
repo = Client(
    prestashop_base_url="https://your-store.com/api",
    prestashop_ws_key="YOUR_API_KEY_HERE",
    max_connections=2,
    max_keepalive_connections=2,
    keepalive_expiry=10.0
)
```

### Basic queries

```python
# Get an order by ID
order = repo.query_order(order_id="12345")

# Check if an order exists
exists = repo.exists_order(order_id="12345")

# Get an address
address = repo.query_address(address_id="67890")

# Get a customer
customer = repo.query_customer(customer_id="123")

# Get a product
product = repo.query_product(product_id="456")

# Get a country
country = repo.query_country(country_id="6")

# Get an order state
order_state = repo.query_order_state(state_id="5")
```

### Queries with parameters

```python
from prestashop_webservice import Params, Sort, SortOrder

# Create query parameters
params = Params(
    filter={"id_customer": "123"},
    sort=Sort(field="date_add", order=SortOrder.DESC),
    display=["id", "total_paid", "reference"],
    limit=10
)

# Get orders with filters
orders = repo.query_orders(params=params)

# Get customers with filters
customers_params = Params(
    filter={"active": "1"},
    display=["id", "email", "firstname", "lastname"],
    limit=50
)
customers = repo.query_customers(params=customers_params)

# Get order history
history_params = Params(
    filter={"id_order": "12345"},
    display=["id_order_state", "date_add"]
)
histories = repo.query_order_histories(params=history_params)

# Get order carriers
carrier_params = Params(
    filter={"id_order": "12345"}
)
carriers = repo.query_order_carriers(params=carrier_params)
```

### Advanced examples

```python
# Search customers by email
email_params = Params(
    filter={"email": "customer@example.com"},
    display=["id", "email"]
)
customers = repo.query_customers(params=email_params)

# Get last 20 orders sorted by date
recent_orders_params = Params(
    sort=Sort(field="date_add", order=SortOrder.DESC),
    display=["id", "reference", "total_paid", "date_add"],
    limit=20
)
recent_orders = repo.query_orders(params=recent_orders_params)

# Search products by category
products_params = Params(
    filter={"id_category_default": "5"},
    display=["id", "name", "price"],
    limit=100
)
products = repo.query_products(params=products_params)
```

## API Reference

### Client

Main class to interact with PrestaShop API.

#### Available methods

##### Orders
- `query_order(params=None, order_id="")` → `dict`
- `query_orders(params=None)` → `list`
- `exists_order(order_id)` → `bool`

##### Customers
- `query_customer(params=None, customer_id="")` → `dict`
- `query_customers(params=None)` → `list`

##### Addresses
- `query_address(params=None, address_id="")` → `dict`

##### Products
- `query_product(params=None, product_id="")` → `dict`

##### Order Carriers
- `query_order_carriers(params=None)` → `dict`

##### Order Histories
- `query_order_histories(params=None)` → `list`

##### Order States
- `query_order_state(params=None, state_id="")` → `dict`

##### Countries
- `query_country(params=None, country_id="")` → `dict`

### Params

Class to build query parameters in a safe and typed way.

```python
@dataclass
class Params:
    filter: dict | None      # Search filters
    sort: Sort | None        # Sorting
    display: list[str] | None  # Fields to display
    limit: int | None        # Result limit
```

### Sort

Class to define sorting.

```python
@dataclass
class Sort:
    field: str          # Field to sort by
    order: SortOrder    # Sort direction (ASC/DESC)
```

### SortOrder

Enumeration for sort order.

```python
class SortOrder(Enum):
    ASC = "ASC"   # Ascending
    DESC = "DESC" # Descending
```

## Cache

All `query_*` methods use automatic caching:

- **TTL (Time To Live)**: 24 hours (86400 seconds) by default
- **Maximum cache size**: Varies by endpoint (50-500 items)
- **Parameter-based cache**: Queries with different parameters are cached separately

## Logger Configuration

The logger is pre-configured with:
- INFO level for console
- DEBUG level for file
- Automatic log rotation (10 MB)
- 10 days retention
- ZIP compression of old logs
- Location: `logs/app.log`

## Development

### Run tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=prestashop_repository --cov-report=html
```

### Format code

```bash
black .
```

### Type checking

```bash
mypy prestashop_repository
```

## Project structure

```
prestashop-webservice/
├── src/
│   ├── __init__.py          # Main exports
│   ├── client.py            # Main Client class
│   ├── params.py           # Parameter models
│   ├── logger.py           # Logging configuration
│   └── py.typed            # Type checking marker
├── tests/                  # Tests (pending)
├── docs/                   # Additional documentation
├── setup.py               # Installation configuration
├── pyproject.toml         # Modern Python configuration
├── requirements.txt       # Dependencies
├── MANIFEST.in           # Files to include in distribution
├── LICENSE               # MIT License
└── README.md             # This file
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

To report bugs or request new features, please open an issue on the GitHub repository.

## Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Changelog

### 0.1.0 (2025-11-13)

- ✨ Initial release
- 🎯 Primitive queries for all main endpoints
- 💾 Integrated cache system
- 📝 Logging with Loguru
- 🔒 Singleton pattern
- 📦 Typed parameter system
