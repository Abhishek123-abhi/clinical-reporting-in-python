"""
Table 1.1.2
Summary of Treatment-Emergent Adverse Events by System Organ Class and Preferred Term
Safety Population
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import rtflite


# ---------------------------------------------------------------------
# Read ADAE and ADSL Datasets
# ---------------------------------------------------------------------

ADAE_PATH = Path(r"C:\Users\aj520\Downloads\adae.xpt")
ADSL_PATH = Path(r"C:\Users\aj520\Downloads\adsl.xpt")

adae, _ = pyreadstat.read_xport(ADAE_PATH)
adsl, _ = pyreadstat.read_xport(ADSL_PATH)


# ---------------------------------------------------------------------
# Create Analysis Datasets
# ---------------------------------------------------------------------

adsl1 = (

    adsl

    .loc[

        adsl["SAFFL"] == "Y",

        [

            "USUBJID",

            "TRT01A"

        ]

    ]

    .copy()

)


adae1 = (

    adae

    .loc[

        (adae["SAFFL"] == "Y")
        &
        (adae["TRTEMFL"] == "Y"),

        [

            "USUBJID",

            "TRT01A",

            "AESOC",

            "AEDECOD"

        ]

    ]

    .copy()

)



# ---------------------------------------------------------------------
# Format Display Values
# ---------------------------------------------------------------------

adae1["AESOC"] = (
    adae1["AESOC"]
    .str.title()
)

adae1["AEDECOD"] = (
    adae1["AEDECOD"]
    .str.title()
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
# Event Summary
# ---------------------------------------------------------------------

def create_event_summary(
    data,
    group_vars,
    big_n,
    decimal=1
):

    if group_vars is None:

        summary = (

            data

            .groupby(
                "TRT01A"
            )

            .agg(
                N=("USUBJID", "nunique")
            )

            .reset_index()

        )

        total = pd.DataFrame(

            {

                "TRT01A": ["Total"],

                "N": [

                    data["USUBJID"].nunique()

                ]

            }

        )

    else:

        summary = (

            data

            .groupby(
                ["TRT01A"] + group_vars,
                dropna=False
            )

            .agg(
                N=("USUBJID", "nunique")
            )

            .reset_index()

        )

        total = (

            data

            .groupby(
                group_vars,
                dropna=False
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

    summary["n (%)"] = (

        summary["N"].astype(str)

        + " ("

        + summary["Percent"].round(decimal).map(
            f"{{:.{decimal}f}}".format
        )

        + ")"

    )

    return summary


# ---------------------------------------------------------------------
# Overall TEAE
# ---------------------------------------------------------------------

overall_summary = create_event_summary(

    data=adae1,

    group_vars=None,

    big_n=big_n

)

print(overall_summary)



# ---------------------------------------------------------------------
# System Organ Class Summary
# ---------------------------------------------------------------------

soc_summary = create_event_summary(

    data=adae1,

    group_vars=["AESOC"],

    big_n=big_n

)

print(soc_summary)



# ---------------------------------------------------------------------
# Preferred Term Summary
# ---------------------------------------------------------------------

pt_summary = create_event_summary(

    data=adae1,

    group_vars=[

        "AESOC",

        "AEDECOD"

    ],

    big_n=big_n

)

print(pt_summary)



# ---------------------------------------------------------------------
# Create TEAE Reporting Table
# ---------------------------------------------------------------------

def create_teae_table(
    overall_summary,
    soc_summary,
    pt_summary,
    treatments
):

    def format_cell(count, denom):

        if count == 0:
            return "0"

        percent = count / denom * 100

        return f"{count} ({percent:.1f})"


    table_rows = []

    # Overall TEAE

    overall_row = {

        "Parameter": "Subjects with at least one TEAE"

    }

    for treatment in treatments:

        result = overall_summary.loc[
            overall_summary["TRT01A"] == treatment
        ]

        count = int(result["N"].iloc[0])
        denom = int(result["N_DENOM"].iloc[0])

        overall_row[treatment] = format_cell(
            count,
            denom
        )

    table_rows.append(overall_row)


    # SOC + PT

    for soc in (

        soc_summary["AESOC"]

        .drop_duplicates()

        .sort_values()

    ):

        soc_row = {

            "Parameter": soc

        }

        for treatment in treatments:

            result = soc_summary.loc[
                (soc_summary["TRT01A"] == treatment)
                &
                (soc_summary["AESOC"] == soc)
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

                count = int(result["N"].iloc[0])

                denom = int(result["N_DENOM"].iloc[0])

            soc_row[treatment] = format_cell(
                count,
                denom
            )

        table_rows.append(soc_row)

        pt_subset = (

            pt_summary

            .loc[
                pt_summary["AESOC"] == soc
            ]

            .sort_values(
                "AEDECOD"
            )

        )

        for pt in (

            pt_subset["AEDECOD"]

            .drop_duplicates()

        ):

            pt_row = {

                "Parameter": f"    {pt}"

            }

            for treatment in treatments:

                result = pt_subset.loc[
                    (pt_subset["TRT01A"] == treatment)
                    &
                    (pt_subset["AEDECOD"] == pt)
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

                    count = int(result["N"].iloc[0])

                    denom = int(result["N_DENOM"].iloc[0])

                pt_row[treatment] = format_cell(
                    count,
                    denom
                )

            table_rows.append(pt_row)

    return pd.DataFrame(table_rows)



# ---------------------------------------------------------------------
# Create Reporting Dataset
# ---------------------------------------------------------------------

teae_table = create_teae_table(

    overall_summary=overall_summary,

    soc_summary=soc_summary,

    pt_summary=pt_summary,

    treatments=big_n["TRT01A"]

)

print(teae_table)




# ---------------------------------------------------------------------
# Add Blank Lines Between Groups
# ---------------------------------------------------------------------

def add_group_spacing(
    df: pd.DataFrame,
    parameter_col: str = "Parameter"
) -> pd.DataFrame:

    rows = []

    first_group = True

    for _, row in df.iterrows():

        parameter = str(row[parameter_col])

        if not parameter.startswith(" "):

            if first_group:

                first_group = False

            else:

                rows.append(
                    {col: "" for col in df.columns}
                )

        rows.append(row.to_dict())

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Insert Blank Lines
# ---------------------------------------------------------------------

teae_table = add_group_spacing(teae_table)

print(teae_table)








# ---------------------------------------------------------------------
# Output Report as RTF File
# ---------------------------------------------------------------------

from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------
# Output File
# ---------------------------------------------------------------------

OUTPUT_RTF = Path(
    r"C:\Users\aj520\Downloads\teae_summary.rtf"
)


# ---------------------------------------------------------------------
# Report Metadata
# ---------------------------------------------------------------------

TABLE_NUMBER = "Table 1.1.2"

TABLE_TITLE = (
    "Summary of Treatment-Emergent Adverse Events"
)

TABLE_SUBTITLE = (
    "by System Organ Class and Preferred Term\n"
    "Safety Population"
)

RUN_DATETIME = (
    f"Run Date: {datetime.now():%d%b%Y %H:%M}"
)


# ---------------------------------------------------------------------
# Column Headers
# ---------------------------------------------------------------------

column_headers = [

    "Parameter",

    f"Placebo\\line(N={big_n.loc[0, 'N']})",

    f"Xanomeline High Dose\\line(N={big_n.loc[1, 'N']})",

    f"Xanomeline Low Dose\\line(N={big_n.loc[2, 'N']})",

    f"Total\\line(N={big_n.loc[3, 'N']})"

]


# ---------------------------------------------------------------------
# Create RTF Document
# ---------------------------------------------------------------------

doc = rtflite.RTFDocument(

    df=teae_table,

    rtf_page=rtflite.RTFPage(

        orientation="landscape",

        margin=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5]

    ),

    rtf_page_header=rtflite.RTFPageHeader(

        text="Page \\chpgn of {\\field{\\*\\fldinst NUMPAGES }}"

    ),

    rtf_page_footer=rtflite.RTFPageFooter(

        text=[

            "Source: ADAE",

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

        ]

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

        border_bottom="single"

    ),

    rtf_body=rtflite.RTFBody(

        col_rel_width=[

            7.5,

            1.5,

            1.5,

            1.5,

            1.5

        ],

        text_justification=[

            [

                "l",

                "c",

                "c",

                "c",

                "c"

            ]

        ],

        border_last="single"

    ),

    rtf_footnote=rtflite.RTFFootnote(

        text=[

            "Abbreviations:",

            "TEAE = Treatment-Emergent Adverse Event.",

            "N = Number of subjects in the treatment group.",

            "n = Number of subjects with at least one event.",

            "Percentages are based on the treatment group denominator (Big N).",

            "",

            "Programming Notes:",

            "• Subjects are counted once within each Preferred Term.",

            "• Subjects are counted once within each System Organ Class.",

            "• A subject with multiple events under the same Preferred Term is counted only once."

        ]

    )

)


# ---------------------------------------------------------------------
# Write RTF File
# ---------------------------------------------------------------------

doc.write_rtf(OUTPUT_RTF)

print(
    f"\nRTF successfully written to:\n{OUTPUT_RTF}"
)