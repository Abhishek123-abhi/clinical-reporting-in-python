# Clinical Reporting in Python

This repository contains example programs demonstrating how **clinical trial output reports (TLFs)** can be developed in **Python** using **rtflite**, an open-source reporting package developed within the **Pharmaverse** ecosystem.

Most clinical programmers are already familiar with developing production-ready TLFs in **SAS** or **R**. While Python has become increasingly popular for data analysis and scientific computing, examples of end-to-end clinical reporting workflows in Python are still relatively limited. This repository aims to provide practical examples for anyone interested in exploring clinical reporting with Python.

The example programs use publicly available **pharmaverseadam** datasets to generate publication-ready **RTF** reports. They are intended as reference implementations for learning, experimentation, and exploring how similar reporting workflows can be developed in Python.

**rtflite** is an open-source Python package for generating Rich Text Format (RTF) documents. Developed within the **Pharmaverse** ecosystem, it brings many of the reporting concepts familiar to **r2rtf** users into Python, making clinical report generation more accessible for Python developers.

---

## Repository Structure

```text
clinical-reporting-in-python/
│
├── data/
│   ├── adsl.xpt
│   └── adae.xpt
│
├── programs/
│   ├── setup.py
│   ├── demographics.py
│   └── teae_summary.py
│
└── output/
    ├── demographics_table.rtf
    └── teae_summary.rtf
```

- **data/** contains the example ADaM datasets.
- **programs/** contains the reporting programs together with a shared `setup.py` used across the examples.
- **output/** contains the generated RTF reports.

---

## Included Examples

- **Table 1.1.1** – Summary of Demographic Characteristics
- **Table 1.1.2** – Summary of Treatment-Emergent Adverse Events by System Organ Class and Preferred Term

---


## Current Scope

The examples in this repository are intended to demonstrate the core workflow for developing clinical TLFs in Python using **rtflite**. While they cover common reporting scenarios, there are several opportunities for further enhancement:

- Additional TLF examples covering a wider range of efficacy and safety analyses.
- More reusable and metadata-driven reporting utilities.
- Enhanced support for complex table layouts and sponsor-specific formatting requirements.
- Integration with other **Pharmaverse** packages as the Python clinical reporting ecosystem continues to evolve.
- Additional examples illustrating best practices for reusable and production-oriented reporting workflows.

## Future Directions

As the Python ecosystem for clinical trial reporting continues to mature, this repository will continue to evolve with additional examples and reusable reporting components.

It is also intended to serve as a useful starting point for clinical programmers who are interested in exploring **Python** for clinical reporting and for anyone looking to build reusable, production-oriented TLF workflows beyond the traditional SAS or R ecosystem.

## References

- **rtflite**  
  https://github.com/pharmaverse/rtflite

- **Pharmaverse**  
  https://pharmaverse.org

- **r2rtf**  
  https://github.com/Merck/r2rtf

- **Pharmaverse ADaM Example Data**  
  https://github.com/pharmaverse/pharmaverseadam
