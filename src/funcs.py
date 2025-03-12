import pandas as pd
import numpy as np

def unit_harm(dat, 
              variable_groups="VariableName",
              unit_colname="UnitCode",
              value_colname="MeasurementValue",
              sample_detect_limit_colname="SampleDetectLimit", 
              method_detect_limit_colname="MethodDetectionLimit"):
    if not isinstance(dat, pd.DataFrame):
        raise ValueError('data must be a dataframe!')
    
    dat2 = []
    
    for i in sorted(dat[variable_groups].dropna().unique()):
        print(i)
        y = dat.loc[dat[variable_groups] == i].copy()
        
        if y[unit_colname].isna().any():
            print(f"Warning: NA exists in {unit_colname} column")

        # skip if there is only one unit
        if y[unit_colname].nunique() == 1:
            dat2.append(y)
            continue

        # Unit conversions
        conversions = {
            ("jtu", "ntu"): (2.5, "ntu"),
            ("mg/m3", "mg/l"): (0.001, "mg/l"),
            ("mg/l", "ug/l"): (1_000, "ug/l"),
            ("mg/l", "ng/l"): (1_000_000, "ng/l"),
            ("ug/l", "ng/l"): (1_000, "ng/l"),
            ("ng/g", "ug/l"): (None, "ug/l"),
            ("no/dl", "no/100 ml"): (None, "no/100 ml"),
            ("rel units", "tcu"): (None, "TCU"),
        }

        for (from_unit, to_unit), (factor, new_unit) in conversions.items():
            if from_unit in y[unit_colname].str.lower().values and to_unit in y[unit_colname].str.lower().values:
                a = y.loc[y[unit_colname].str.lower() == from_unit].copy()
                b = y.loc[y[unit_colname].str.lower() != from_unit].copy()
                if factor is not None:
                    a[value_colname] *= factor
                    a[sample_detect_limit_colname] *= factor
                    a[method_detect_limit_colname] *= factor
                a[unit_colname] = new_unit
                y = pd.concat([a, b], ignore_index=True)

        my_unit = y[unit_colname].dropna().unique()
        
        if len(my_unit) > 1:
            print(f"Warning: There are still multiple units: {', '.join(my_unit)}")

        dat2.append(y)
    
    return pd.concat(dat2, ignore_index=True) if dat2 else pd.DataFrame()