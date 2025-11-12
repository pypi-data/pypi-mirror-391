import json
from collections import defaultdict
from typing import Dict

from fuzzywuzzy import fuzz, process

from factly.standard_names.states import check_state_names
from factly.standard_names.utils import get_district_code_data


def check_district_names(dfObj, std_data, district_col):
    district_names = dfObj[district_col].unique().tolist()
    std_district_names = std_data["district_as_per_source"].unique().tolist()
    improper_districts = set(district_names) - set(std_district_names)
    if improper_districts:
        print(
            "There are improper district names in the dataframe, fix them and run the script again"
        )
        print(f"Improper district names: {improper_districts}")
        return False
    return True


def add_district_code(dfObj, district_col, identifier="None"):
    """
    Adds district codes to the dataframe.
    only if district names are correct.
    """

    std_data = get_district_code_data()

    district_col_loc = dfObj.columns.get_loc(district_col)
    dfObj.insert(
        district_col_loc + 2,
        "district_lgd_code",
        dfObj[district_col].map(
            std_data.set_index("district_as_per_source")["district_lgd_code"].to_dict()
        ),
    )

    if dfObj["district_lgd_code"].isnull().any():
        district_with_no_code = (
            dfObj[dfObj["district_lgd_code"].isnull()][district_col].unique().tolist()
        )
        print("LGD codes not found for districts")
        logs = {identifier: {"district_with_no_code": district_with_no_code}}
        with open("standard_names.log", "a+") as f:
            f.write(json.dumps(logs) + "\n")

    dfObj["district_lgd_code"] = dfObj["district_lgd_code"].astype("Int64")
    return dfObj


def standardise_district_names(
    dfObj,
    state_col,
    district_col,
    thresh=70,
    manual_changes: Dict[str, Dict[str, str]] = {},
    identifier="None",
):
    """
    find all improper district names from a given dataframe
    and replaces it with standard names proved.
    dfObj : DataFrame object on which district names should be standardize
    district_col : name of column which has entries as district names
    manual_changes : Dict[str, Dict[str, str]] , default : null dict , changes in names done manually.
    """
    std_data = get_district_code_data()
    if not check_state_names(dfObj, std_data, state_col):
        return dfObj
    dfObj.rename(columns={district_col: "district_as_per_source"}, inplace=True)

    # Dictionaries will have key value pair as improper and proper name
    logs = defaultdict(dict)
    changes = defaultdict(dict)
    corrupt = defaultdict(dict)

    unique_state_names = dfObj["state"].unique().tolist()
    for state_name in unique_state_names:
        std_districts = (
            std_data[std_data["state"] == state_name]["district_as_per_source"]
            .unique()
            .tolist()
        )
        improper_districts = (
            dfObj[dfObj["state"] == state_name]["district_as_per_source"]
            .unique()
            .tolist()
        )
        for district in improper_districts:
            if isinstance(district, str):
                district = district.strip()
            else:
                district = ""
            match = process.extract(
                district, std_districts, scorer=fuzz.token_set_ratio
            )
            if len(match) ==1:
                changes[state_name][district] = match[0][0]

            elif (match[0][1] == match[1][1]):
                if district not in manual_changes.get(state_name, {}).keys():
                    corrupt[state_name][district] = ""
                    
            elif (match[0][1] >= thresh and match[0][1] >= match[1][1] + 1):
                changes[state_name][district] = match[0][0]
            else:
                if district not in manual_changes.get(state_name, {}).keys():
                    corrupt[state_name][district] = ""
                    
    for state_name, district_changes in manual_changes.items():
        changes[state_name].update(district_changes)

    if bool(corrupt):
        print(
            "There are improper district names that function can't fix.\nPlease refer to logs.json."
        )
    logs.update({identifier: {"changes": changes, "corrupt": corrupt}})

    with open("standard_names.log", "a+") as log_file:
        log_file.write(json.dumps(logs) + "\n")

    # replace values in the dataframe
    for state_name, district_changes in changes.items():
        dfObj.loc[dfObj["state"] == state_name, "district_as_per_source"] = dfObj.loc[
            dfObj["state"] == state_name, "district_as_per_source"
        ].map(district_changes)

    district_col_loc = dfObj.columns.get_loc("district_as_per_source")
    dfObj.insert(
        district_col_loc + 1,
        "district_as_per_lgd",
        dfObj["district_as_per_source"].map(
            std_data.set_index("district_as_per_source")[
                "district_as_per_lgd"
            ].to_dict()
        ),
    )

    dfObj = add_district_code(dfObj, "district_as_per_source", identifier)

    if "note" in dfObj.columns:
        note_var = "note"
    elif 'notes' in dfObj.columns:
        note_var = "notes"
    mask = dfObj[note_var].isna()
    dfObj.loc[mask, note_var] = dfObj.loc[mask, "district_as_per_source"].map(
            std_data.set_index("district_as_per_source")["notes"].to_dict()
        )
    dfObj.loc[~mask, note_var] = (
            dfObj.loc[~mask, note_var]
            + ", "
            + dfObj.loc[~mask, "district_as_per_source"].map(
                std_data.set_index("district_as_per_source")["notes"].to_dict()
            )
        )

    return dfObj
