# Proxy Manager 

A package for managing free proxies from various sources, validating their operability, and filtering them based on criteria.  Intended as way of automatically obtaining a working proxy from a various lists,

## Features
- Download proxies from various sources. 
- Validate proxies for operability. - Filter proxies based on criteria. 
- Added command-line interface using `click`.


## Installation 

To install the package, using `poetry`:

```bash
git clone https://github.com/ajanderson1/free-proxy-manager
cd free-proxy-manager
poetry install
```


## Usage

### As a Library

You can use the `ProxyManager` class directly in your Python code to download, filter, and validate proxies.

```python
from free_proxy_manager.proxy_manager import ProxyManager

# Initialize ProxyManager
proxy_manager = ProxyManager(source='free-proxy-list.net', timeout=5)

# List all proxies
proxies = proxy_manager.list_proxies()
print(proxies)

# Filter proxies
filtered_proxies = proxy_manager.filter_proxies(filter_by={'country': 'US', 'https': 'yes'})
print(filtered_proxies)

# Return n operational proxies
operational_proxies = proxy_manager.return_n_operational_proxies(n=2, filter_by={'country': 'US', 'https': 'yes'})
print(operational_proxies)
```

### Command-Line Interface (CLI)

The package includes a CLI for easy access to its functionalities.

#### Basic Command

`poetry run proxy-manager --source 'free-proxy-list.net' --n 2 --timeout 5 --max_threads 10 --randomise`

#### Options

- `--source`: Source of proxies (default: 'free-proxy-list.net').
  
- `--n`: Number of operational proxies to return (default: 1).
  
- `--timeout`: Timeout for proxy validation (default: 5).
  
- `--filter_by`: Filter for proxies in the form key:value,key:value (default: None).
  
- `--max_threads`: Maximum number of threads for validation (default: 10).
  
- `--randomise/--no-randomise`: Randomise the order of proxies before validation (default: randomise).
  
- `--log_level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (default: INFO).
  
- `--log_file`: Log to a file instead of standard output.
  

#### Examples

- **Log to the console with DEBUG level**:
  
  `poetry run proxy-manager --source 'free-proxy-list.net' --n 2 --timeout 5 --filter_by 'country:United States,https:yes' --max_threads 10 --log_level DEBUG`
  

## Configuration

The configuration settings for the proxy sources and validation can be found in the `config.py` file. Modify these settings according to your requirements.

## Development

To contribute to this project:

1. Clone the repository.
2. Install dependencies using `poetry install`.
3. Create a new branch for your feature or bugfix.
4. Submit a pull request with your changes.
