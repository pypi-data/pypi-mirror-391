# ReqSim - Lightweight API Benchmarking Tool

## Description

ReqSim is a lightweight Python package designed for benchmarking and load testing APIs using asynchronous HTTP requests. It provides developers with quick insights into API performance without the complexity of heavy tools like JMeter or Postman.  Ideal for rapid performance checks and identifying bottlenecks in your API.

## Key Features & Benefits

-   **Asynchronous Requests:** Leverage `aiohttp` for efficient concurrent requests.
-   **Simple CLI Interface:** Easy-to-use command-line interface for quick testing.
-   **Concise Output:** Clear summary of request statistics, including average response time and status codes.
-   **Lightweight & Portable:** No complex setup or dependencies beyond `aiohttp`.
-   **Rapid Insights:** Get immediate feedback on API performance.

## Prerequisites & Dependencies

-   Python 3.8 or higher
-   `aiohttp`

## Installation & Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone <repository_url> # Replace with your repository URL
    cd ReqSim
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```

3.  **Install ReqSim from `setup.py`:**

    ```bash
    python setup.py install
    ```

    Alternatively, install from PyPI after it is published.

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage Examples & API Documentation

### Command-Line Interface (CLI)

The main entry point is the `reqsim` command.

**Basic Usage:**

```bash
reqsim <URL>
```

This sends 10 GET requests to the specified URL by default and prints a summary.

**Options:**

-   `-n` or `--num`: Number of requests to send (default: 10).
-   `-X` or `--method`: HTTP method to use (default: GET).
-   `-d` or `--data`: Request body data (string).

**Example with POST request and data:**

```bash
reqsim https://example.com/api/endpoint -n 50 -X POST -d '{"key": "value"}'
```

This sends 50 POST requests with the provided JSON data to the specified URL.

### Example Output

```
URL: https://example.com/api/endpoint
Requests: 10
Average Response Time: 0.123 seconds
Status Code Distribution:
    200: 10
```

### Python API Usage

```python
import asyncio
from reqsim.core import simulate, summarize, run_requests

async def main():
    url = "https://example.com/api/endpoint"
    num_requests = 20
    method = "GET"
    data = None

    results = await run_requests(url, num_requests, method, data)
    summary = summarize(results)

    print(summary)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Options

ReqSim primarily uses command-line arguments for configuration.  The number of requests, HTTP method, and request body data can all be configured via the CLI. No specific environment variables are currently utilized.

## Contributing Guidelines

Contributions are welcome!  Here's how you can contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Implement your changes.
4.  Add tests to ensure your changes work as expected.
5.  Submit a pull request with a clear description of your changes.

## License Information

License information is currently not specified. Please contact the repository owner (Alanperry1) for licensing details.

## Acknowledgments

-   This project utilizes the `aiohttp` library for asynchronous HTTP requests.