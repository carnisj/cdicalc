CDICALC: GUI for setup calculations in Coherent X-ray Diffraction Imaging experiments.
======================================================================================

Calculations are performed using the
`pint package <https://pint.readthedocs.io/en/stable/>`_, to remove any ambiguity about
units.

Installation:
-------------

- ``git clone https://github.com/carnisj/cdicalc.git``
- (Optional) Create a virtual environment (Python3.9) and activate it
- ``cd cdicalc/``
- ``pip install -r requirements.txt``

Usage:
------

- ``cd scripts/``
- ``python cdicalc_client.py``

The script ``cdicalc_client.py`` will also be copied in (e.g. for a Conda environment):

- on Windows: ``path_to\anaconda3\envs\myenv\Scripts``

- on Linux: ``/path_to/anaconda3/envs/myenv/bin``


