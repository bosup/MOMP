def dim_fmt(ds):
    """Standardize dimension names"""
    coord_list = list(ds.coords.keys())

    if "lon" not in coord_list:
        print("lon NOT in coords  --> ")  # , model_name)
        lat_coords = [variable for variable in coord_list if "lat" in variable.lower()][0]
        lon_coords = [variable for variable in coord_list if "lon" in variable.lower()][0]

        ds = ds.rename({lat_coords: "lat", lon_coords: "lon"})

    if "time" not in coord_list:
        print("time NOT in coords --> ")  # , model_name)
        time_coords = [variable for variable in coord_list if "TIME" in variable][0]
        ds = ds.rename({time_coords: "time"})

    return ds


def dim_fmt_model(ds):
    """Standardize dimension names for reforecast model data"""
    coord_list = list(ds.coords.keys())

    if "lon" not in coord_list:
        print("lon NOT in coords  --> ")  # , model_name)
        lat_coords = [variable for variable in coord_list if "lat" in variable.lower()][0]
        lon_coords = [variable for variable in coord_list if "lon" in variable.lower()][0]

        ds = ds.rename({lat_coords: "lat", lon_coords: "lon"})

    if "init_time" not in coord_list:
        print("init_time NOT in coords --> ")  # , model_name)
        time_coords = [variable for variable in coord_list if "time" in variable.lower()][0]
        ds = ds.rename({time_coords: "init_time"})


    if "member" not in coord_list:
        keywords = ["number", "sample"]
        ensemble_coords = [
            variable
            for variable in coord_list
            if any(keyword in variable.lower() for keyword in keywords)
        ]
        ds = ds.rename({ensemble_coords: "member"})


    if "step" not in coord_list:
        keywords = ["day"]
        step_coords = [
            variable
            for variable in coord_list
            if any(keyword in variable.lower() for keyword in keywords)
        ]
        ds = ds.rename({step_coords: "step"})

    return ds


##case
#unit_cvt
#var_name


