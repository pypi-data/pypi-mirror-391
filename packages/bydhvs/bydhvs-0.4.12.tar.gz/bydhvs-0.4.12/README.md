# python-bydhvs
Python Wrapper for BYD b-Box HVM/HVS/LVS

This is a python module to communicate with an BYD HVM/HVS/LVS.

inspired by (https://github.com/christianh17/ioBroker.bydhvs)

If used with **BYD Be Connect** at the same time. This module is **not** working correctly.

Tested with 2 Towers and 5 Modules. Thx @st0ne-dot-at

Installation
------------
The module is available from the [Python Package Index](https://pypi.python.org/pypi)


    $ pip3 install bydhvs

On a Fedora-based system or a CentOS/RHEL host with EPEL.

    $ sudo dnf -y install python3-bydhvs

Usage
-----

The file ``example.py`` contains an example about how to use this module.

Build
-----
To build dev prepare system:

    $ python -m pip install --upgrade pip
    $ pip install build

build package:
  
    $ python -m build

License
-------

``python-byd`` is licensed under GPL-3.0 license, for more details check LICENSE.
