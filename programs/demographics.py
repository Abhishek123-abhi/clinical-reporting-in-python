"""
Table 1.1.1
Summary of Demographic Characteristics
Safety Population
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import rtflite


# ---------------------------------------------------------------------
# Read ADSL Dataset
# ---------------------------------------------------------------------

ADSL_PATH = Path(r"C:\Users\aj520\Downloads\adsl.xpt")

adsl, _ = pyreadstat.read_xport(ADSL_PATH)



# ---------------------------------------------------------------------
# Create Analysis Dataset
# ---------------------------------------------------------------------

adsl1 = (
    adsl
    .loc[
        adsl["SAFFL"] == "Y",
        [
            "USUBJID",
            "TRT01A",
            "AGE",
            "SEX",
            "RACE",
            "ETHNIC"
        ]
    ]
    .copy()
)



# ---------------------------------------------------------------------
# Treatment Group Counts (Big N)
# ---------------------------------------------------------------------

big_n = (
    adsl1
    .groupby("TRT01A", dropna=False)
    .agg(
        N=("USUBJID", "nunique")
    )
    .reset_index()
)

total_n = pd.DataFrame(
    {
        "TRT01A": ["Total"],
        "N": [adsl1["USUBJID"].nunique()]
    }
)

big_n = pd.concat(
    [big_n, total_n],
    ignore_index=True
)

print(big_n)




# ---------------------------------------------------------------------
# AGE Summary (Continuous)
# ---------------------------------------------------------------------
age_summary = (
    adsl1
    .groupby("TRT01A")
    .agg(
        N=("AGE", "count"),
        Mean=("AGE", "mean"),
        SD=("AGE", "std"),
        Median=("AGE", "median"),
        Minimum=("AGE", "min"),
        Maximum=("AGE", "max")
    )
    .reset_index()
)

print(age_summary)


age_total = pd.DataFrame(
    {
        "TRT01A": ["Total"],
        "N": [adsl1["AGE"].count()],
        "Mean": [adsl1["AGE"].mean()],
        "SD": [adsl1["AGE"].std()],
        "Median": [adsl1["AGE"].median()],
        "Minimum": [adsl1["AGE"].min()],
        "Maximum": [adsl1["AGE"].max()]
    }
)

age_summary = pd.concat(
    [age_summary, age_total],
    ignore_index=True
)

print(age_summary)



# Format AGE Statistics

age_summary["Mean (SD)"] = (
    age_summary["Mean"].round(1).map("{:.1f}".format)
    + " ("
    + age_summary["SD"].round(2).map("{:.2f}".format)
    + ")"
)

age_summary["Median"] = (
    age_summary["Median"].round(1).map("{:.1f}".format)
)

age_summary["Min, Max"] = (
    age_summary["Minimum"].round(0).astype(int).astype(str)
    + ", "
    + age_summary["Maximum"].round(0).astype(int).astype(str)
)

print(age_summary)




# AGE Section


age_section = pd.DataFrame(
    {
        "Parameter": [
            "Age (Years)",
            "  N",
            "  Mean (SD)",
            "  Median",
            "  Min, Max"
        ]
    }
)


for treatment in age_summary["TRT01A"]:

    subset = age_summary.loc[
        age_summary["TRT01A"] == treatment
    ].iloc[0]

    age_section[treatment] = [
        "",
        str(subset["N"]),
        subset["Mean (SD)"],
        subset["Median"],
        subset["Min, Max"]
    ]

print(age_section)





# ---------------------------------------------------------------------
# Categorical Summary
# ---------------------------------------------------------------------

def create_categorical_section(
    data,
    variable,
    section_title,
    categories,
    big_n,
    decimal=1
):

    # Summary

    summary = (

        data

        .groupby(
            ["TRT01A", variable]
        )

        .agg(
            N=("USUBJID", "nunique")
        )

        .reset_index()

    )


    # Total

    total = (

        data

        .groupby(
            variable
        )

        .agg(
            N=("USUBJID", "nunique")
        )

        .reset_index()

    )

    total["TRT01A"] = "Total"

    summary = pd.concat(

        [

            summary,

            total

        ],

        ignore_index=True

    )


    # Calculate Percentage

    summary = summary.merge(

        big_n,

        on="TRT01A",

        how="left",

        suffixes=("", "_DENOM")

    )

    summary["Percent"] = (

        summary["N"]

        / summary["N_DENOM"]

        * 100

    )


    # -------------------------------------------------------------
    # Format Display Value
    # -------------------------------------------------------------

    def format_cell(
        count,
        denom
    ):

        if count == 0:

            return "0"

        percent = count / denom * 100

        return f"{count} ({percent:.{decimal}f})"


    # Create Section

    section = pd.DataFrame(

        {

            "Parameter":

                [section_title]

                + ["  " + category for category in categories]

        }

    )


    # Populate Section

    for treatment in big_n["TRT01A"]:

        subset = summary.loc[

            summary["TRT01A"] == treatment

        ]

        values = [""]

        for category in categories:

            result = subset.loc[

                subset[variable] == category

            ]

            if result.empty:

                count = 0

                denom = int(

                    big_n.loc[

                        big_n["TRT01A"] == treatment,

                        "N"

                    ].iloc[0]

                )

            else:

                count = int(

                    result["N"].iloc[0]

                )

                denom = int(

                    result["N_DENOM"].iloc[0]

                )

            values.append(

                format_cell(

                    count,

                    denom

                )

            )

        section[treatment] = values

    return section



# sex
sex_section = create_categorical_section(
    data=adsl1,
    variable="SEX",
    section_title="Sex, n (%)",
    categories=[
        "F",
        "M"
    ],
    big_n=big_n
)


# race
race_section = create_categorical_section(
    data=adsl1,
    variable="RACE",
    section_title="Race, n (%)",
    categories=[
        "WHITE",
        "BLACK OR AFRICAN AMERICAN",
        "ASIAN",
        "AMERICAN INDIAN OR ALASKA NATIVE",
        "MULTIPLE"
    ],
    big_n=big_n
)


# ethnic
ethnic_section = create_categorical_section(
    data=adsl1,
    variable="ETHNIC",
    section_title="Ethnicity, n (%)",
    categories=[
        "HISPANIC OR LATINO",
        "NOT HISPANIC OR LATINO"
    ],
    big_n=big_n
)



# ----------------------------------------------------
# Final table
# ----------------------------------------------------
demographics_table = pd.concat(
    [
        age_section,
        sex_section,
        race_section,
        ethnic_section
    ],
    ignore_index=True
)



# ----------------------------------------------------
# Display Logic
# ----------------------------------------------------


# Race
demographics_table["Parameter"] = (
    demographics_table["Parameter"]
    .str.replace(r"^(\s*)WHITE$", r"\1White", regex=True)
    .str.replace(r"^(\s*)BLACK OR AFRICAN AMERICAN$", r"\1Black or African American", regex=True)
    .str.replace(r"^(\s*)ASIAN$", r"\1Asian", regex=True)
    .str.replace(r"^(\s*)AMERICAN INDIAN OR ALASKA NATIVE$", r"\1American Indian or Alaska Native", regex=True)
    .str.replace(r"^(\s*)MULTIPLE$", r"\1Multiple", regex=True)
)

# Ethnicity
demographics_table["Parameter"] = (
    demographics_table["Parameter"]
    .str.replace(r"^(\s*)HISPANIC OR LATINO$", r"\1Hispanic or Latino", regex=True)
    .str.replace(r"^(\s*)NOT HISPANIC OR LATINO$", r"\1Not Hispanic or Latino", regex=True)
)



# ---------------------------------------------------------------------
# Add Blank Lines Between Groups
# ---------------------------------------------------------------------

import pandas as pd


def add_group_spacing(
    df: pd.DataFrame,
    parameter_col: str = "Parameter"
) -> pd.DataFrame:

    rows = []

    first_group = True

    for _, row in df.iterrows():

        if not str(row[parameter_col]).startswith(" ") and not first_group:

            rows.append(
                {col: "" for col in df.columns}
            )

        rows.append(row.to_dict())

        if not str(row[parameter_col]).startswith(" "):
            first_group = False

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Insert Blank Lines
# ---------------------------------------------------------------------

demographics_table = add_group_spacing(
    demographics_table
)

print(demographics_table)



# ---------------------------------------------------------------------
# Output report as RTF file
# ---------------------------------------------------------------------


import inspect
import rtflite

print(inspect.signature(rtflite.RTFBody))
print(inspect.signature(rtflite.RTFColumnHeader))



from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------
# Output File
# ---------------------------------------------------------------------

OUTPUT_RTF = Path(
    r"C:\Users\aj520\Downloads\demographics_table.rtf"
)

# ---------------------------------------------------------------------
# Report Metadata
# ---------------------------------------------------------------------

TABLE_NUMBER = "Table 1.1.1"
TABLE_TITLE = "Summary of Demographic Characteristics"
TABLE_SUBTITLE = "Safety Population"

RUN_DATETIME = f"Run Date: {datetime.now():%d%b%Y %H:%M}"

# ---------------------------------------------------------------------
# Column Headers
# ---------------------------------------------------------------------

column_headers = [

    "Parameter",

    f"Placebo\n(N={big_n.loc[0, 'N']})",

    f"Xanomeline High Dose\n(N={big_n.loc[1, 'N']})",

    f"Xanomeline Low Dose\n(N={big_n.loc[2, 'N']})",

    f"Total\n(N={big_n.loc[3, 'N']})"

]

# ---------------------------------------------------------------------
# Create RTF Document
# ---------------------------------------------------------------------

doc = rtflite.RTFDocument(

    df=demographics_table,

    rtf_page=rtflite.RTFPage(

        orientation="landscape",

        margin=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

    ),

    rtf_page_header=rtflite.RTFPageHeader(

        text="Page \\chpgn of {\\field{\\*\\fldinst NUMPAGES }}"

    ),

    rtf_page_footer=rtflite.RTFPageFooter(

        text=[

            "Source: ADSL",

            "Company Confidential",

            RUN_DATETIME

        ],

        text_justification=[

            "l",

            "c",

            "r"

        ],

        text_font_size=[

            8,

            8,

            8

        ]

    ),

    rtf_title=rtflite.RTFTitle(

        text=[

            TABLE_NUMBER,

            TABLE_TITLE,

            TABLE_SUBTITLE

        ],

        text_format=["", "", ""]

    ),

    rtf_column_header=rtflite.RTFColumnHeader(

        text=column_headers,

        text_format="b",

        text_justification=[

            "l",

            "c",

            "c",

            "c",

            "c"

        ],

        border_top="",

        border_bottom="single"

    ),

    rtf_body=rtflite.RTFBody(

        col_rel_width=[5.5, 1.5, 1.5, 1.5, 1.5],

        text_justification=[

            [

                "l",

                "c",

                "c",

                "c",

                "c"

            ]

        ],

        border_left="",

        border_right="",

        border_top="",

        border_bottom="",

        border_first="",

        border_last="single"

    ),

    rtf_footnote=rtflite.RTFFootnote(

        text=[

            "N = Number of subjects in the treatment group.",

            "Percentages are based on the treatment group denominator (Big N).",

            "",

            "Abbreviations: SD = Standard Deviation."

        ]

    )

)

# ---------------------------------------------------------------------
# Write RTF
# ---------------------------------------------------------------------

doc.write_rtf(OUTPUT_RTF)

print(f"\nRTF successfully written to:\n{OUTPUT_RTF}")