# amzsc

[![image](https://img.shields.io/pypi/v/amzsc.svg)](https://pypi.python.org/pypi/amzsc)
[![image](https://img.shields.io/pypi/l/amzsc.svg)](https://img.shields.io/pypi/l/amzsc.svg)
[![image](https://img.shields.io/pypi/pyversions/amzsc.svg)](https://img.shields.io/pypi/pyversions/amzsc.svg)
[![Actions status](https://github.com/ryzanbui02/amzsc/actions/workflows/test-and-release.yaml/badge.svg)](https://github.com/ryzanbui02/amzsc/actions)
[![codecov](https://codecov.io/gh/ryzanbui02/amzsc/branch/main/graph/badge.svg)](https://codecov.io/gh/ryzanbui02/amzsc)

`amzsc` is an Amazon product description scraper library that allows you to extract product details such as title, price, description, and reviews using ASINs.

## Example Usage

```python
from amzsc import AmazonScraper


def main():
    # Initialize the AmazonScraper with your Amazon credentials
    scraper = AmazonScraper()
    asins = ['B08N5WRWNW', 'B07XJ8C8F5']  # Example ASINs
    results = scraper.scrape(asins=asins, marketplace="US") # DataFrame with scraped data
    print(results)


if __name__ == "__main__":
    main()
```

## Installation

```bash
pip install amzsc
```

## Contribution

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

```bash
git clone https://github.com/ryzanbui02/amzsc.git
cd amzsc
uv sync
```
