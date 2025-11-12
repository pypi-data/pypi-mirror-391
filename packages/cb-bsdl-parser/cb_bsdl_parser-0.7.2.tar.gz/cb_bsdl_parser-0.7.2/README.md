<h1 align="center">
Chriesibaum's BSDL File Parser

[![pypi](https://img.shields.io/pypi/v/cb_bsdl_parser.svg)](https://pypi.org/project/cb_bsdl_parser/)
[![python](https://img.shields.io/pypi/pyversions/cb_bsdl_parser.svg)](https://pypi.org/project/cb_bsdl_parser/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/cb_bsdl_parser)](https://pypi.org/project/cb_bsdl_parser/)
[![GitHub stars](https://img.shields.io/github/stars/chriesibaum/cb_bsdl_parser.svg)](https://github.com/smarie/python-genbadge/stargazers)
<br>
[![Tests Status](https://raw.githubusercontent.com/chriesibaum/cb_bsdl_parser/refs/heads/main/doc/tests-badge.svg)]()
[![Coverage Status](https://raw.githubusercontent.com/chriesibaum/cb_bsdl_parser/refs/heads/main/doc/coverage-badge.svg)]()

</h1>


When I was tinkering around with JTAG and BSDL files, I realized that there was no truly functional BSDL file parser for Python. Perhaps I simply didn't search hard enough. In any case, many packages are no longer up to date or have broken dependencies. Let's get our hands dirty - a few moments later and here is what I needed. If you can use it too, I'm happy to receive any inputs.

## Basic usage:
Download and install the package from [pypi.org](https://pypi.org/project/cb-bsdl-parser/). It's recommended to install the package into a virtual Python environment.

```
pip install cb_bsdl_parser
```

There are two tools available to examine BSDL files:
- cb_bsdl_check: To check a BSDL file
- cb_bsdl_info: To get basic data and info from a BSDL file

```
cb_bsdl_check <bsdl_file> [options]
```

```
cb_bsdl_info <bsdl_file> [--cell CELL] [--print-bsr-table]
```

To use it in your Python project, create a BSDL object and extract the needed data:

```
bsdl = CBBsdl('bsdl_file.bsdl')

bsdl.get_entity_name()

# get the pin mapping as a dict:
pin_map = bsdl.get_pin_map()

# or just print the boundary scan table:
bsdl.print_bsr_table()
```

There is a handful of more methods available to extract other data from the BSDL file.

## Development

### Dev tool installation

The development is mainly being done on an Ubuntu 24.04 box. To set up a dev environment, use Python 3 and install the following packages:
```
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

To use ```antlr4```, install it from the deb package sources/store:

```
sudo apt install antlr4
```


## About Café - The source of coding! ;-)

Do you like this project and would like to support it? I am delighted about every single Café- It keeps me running! Or would you sponsor the project on [github sponsors](https://github.com/sponsors/chriesibaum/)? Thanks for your support!

<div align="center">
<a href="https://www.buymeacoffee.com/chriesibaum" target="_blank">
<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

</div>