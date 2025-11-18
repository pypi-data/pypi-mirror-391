# clockitpy �

A small Python library to measure function execution time easily.

## Installation

```bash
pip install clockitpy
```

## Usage

### Using as a decorator

```python
from clockitpy import measure_time

@measure_time
def my_function():
    # Your code here
    sum([i for i in range(1000000)])

my_function()
# Output: my_function executed in 0.045123 seconds
```

### Using timeit function

```python
from clockitpy import timeit

def my_function():
    return sum([i for i in range(1000000)])

duration, result = timeit(my_function)
print(f"Execution time: {duration:.6f} seconds")
print(f"Result: {result}")
```

## Features

- **measure_time**: A decorator to automatically measure and print execution time
- **timeit**: A function to measure execution time and get both duration and result

## Requirements

- Python >= 3.7

## License

MIT License - see LICENSE file for details
