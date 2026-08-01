"""
Project Setup

Author: Abhishek K. Jaiswal

This script loads the Pharmaverse ADaM sample datasets used throughout
this repository. Update the file paths below to match the location of
your ADSL and ADAE XPT files before running the reporting examples.
"""

from pathlib import Path
import pandas as pd
import pyreadstat
import numpy as np
import rtflite
import polars as pl



# Dataset Paths


ADSL_PATH = Path(r"C:\Users\aj520\Downloads\adsl.xpt")
ADAE_PATH = Path(r"C:\Users\aj520\Downloads\adae.xpt")



# Load Datasets


adsl, _ = pyreadstat.read_xport(ADSL_PATH)
adae, _ = pyreadstat.read_xport(ADAE_PATH)



# Dataset Summary


print(f"ADSL: {adsl.shape[0]} rows × {adsl.shape[1]} columns")
print(f"ADAE: {adae.shape[0]} rows × {adae.shape[1]} columns")


# View dataset
print("\nADSL")
print(adsl.head(20))

print("\nADAE")
print(adae.head(20))



print(adsl.columns.tolist())
print(adae.columns.tolist())