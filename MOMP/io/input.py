import importlib.resources
from MOMP.utils

def set_dir(folder):
    """
    set absolute directory path for a specific folder in MOMP
    """
    package = "MOMP"
    base_dir = importlib.resources.files(package)
    target_dir = (base_dir / folder).resolve()

    return target_dir


def load_thresh_file(thresh_file, **kwargs):
    if thresh_file:
        thresh_ds = xr.open_dataset(thresh_file)
        thresh_da = thresh_ds[kwargs["thresh_var"]]

    #elif np.isscalar(thresh_file):
    else:
        thresh_da = kwargs["wet_threshold"]

    return thresh_da


def get_initialization_dates(year, **kwargs):
    """
    Get initialization dates (Mondays and Thursdays from May-July) for a given year.
    """
    date_filter_year = kwargs['date_filter_year']
    init_days = kwargs["init_days"]
    start_MMDD = kwargs["start_date"][1:]
    end_MMDD = kwargs["end_date"][1:]

    start_date = datetime(date_filter_year, *start_MMDD)
    end_date = datetime(date_filter_year, *end_MMDD)
    date_range = pd.date_range(start_date, end_date, freq='D')

    filtered_dates = date_range[date_range.weekday.isin(init_days)]

    # Convert to the requested year
    filtered_dates_yr = pd.to_datetime(filtered_dates.strftime(f'{year}-%m-%d'))

    return filtered_dates_yr


def load_imd_rainfall(year, imd_folder, **kwargs):
    """Load IMD daily rainfall NetCDF for a given year."""
    file_patterns = [f"data_{year}.nc", f"{year}.nc"]

    imd_file = None
    for pattern in file_patterns:
        test_path = f"{imd_folder}/{pattern}"
        if os.path.exists(test_path):
            imd_file = test_path
            break

    if imd_file is None:
        available_files = [f for f in os.listdir(imd_folder) if f.endswith('.nc')]
        raise FileNotFoundError(
            f"No IMD file found for year {year} in {imd_folder}. "
            f"Tried patterns: {file_patterns}. "
            f"Available files: {available_files}"
        )

    print(f"Loading IMD rainfall from: {imd_file}")

    ds = xr.open_dataset(imd_file)
    rainfall = ds['RAINFALL']

    # Standardize dimension names
    dim_mapping = {}
    # Check for latitude/longitude dimensions
    if 'latitude' in rainfall.dims:
        dim_mapping['latitude'] = 'lat'
    if 'LATITUDE' in rainfall.dims:
        dim_mapping['LATITUDE'] = 'lat'
    if 'longitude' in rainfall.dims:
        dim_mapping['longitude'] = 'lon'
    if 'LONGITUDE' in rainfall.dims:
        dim_mapping['LONGITUDE'] = 'lon'
    if 'TIME' in rainfall.dims:
        dim_mapping['TIME'] = 'time'

    if dim_mapping:
        rainfall = rainfall.rename(dim_mapping)
        print(f"Renamed dimensions: {dim_mapping}")

    return rainfall


# var='tp', unit_cvt=, date_filter_year=2024
def get_forecast_deterministic_twice_weekly(yr, model_forecast_dir, file_pattern='{}.nc', **kwargs):
    """
    Loads model precip data for twice-weekly initializations from May to July.
    Filters for Mondays and Thursdays in the specified year.
    The forecast file is expected to be named as '{year}.nc' in the model_forecast_dir with
    variable "tp" being daily accumulated rainfall with dimensions (init_time, lat, lon, step).

    Parameters:
    yr: int, year to load data for

    Returns:
    p_model: ndarray, precipitation data
    """

    date_filter_year = kwargs['date_filter_year']
    init_days = kwargs["init_days"]
    start_MMDD = kwargs["start_date"][1:]
    end_MMDD = kwargs["end_date"][1:]

    fname = file_pattern.format(yr)
    file_path = os.path.join(model_forecast_dir, fname)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Filter for twice weekly data from daily for the specified year based on 2024 Monday and Thursday dates (to match with IFS CY48R1 reforecasts)
    # Define date range from May 1 to July 31 of 2024
#    start_date = datetime(date_filter_year, *start_MMDD)
#    end_date = datetime(date_filter_year, *end_MMDD)
#    date_range = pd.date_range(start_date, end_date, freq='D')
#
#    # Find Mondays (weekday=0) and Thursdays (weekday=3) in pandas
#    #is_monday = date_range.weekday == 0
#    #is_thursday = date_range.weekday == 3
#    #filtered_dates = date_range[is_monday | is_thursday]
#    filtered_dates = date_range[date_range.weekday.isin(init_days)]
#
#    filtered_dates_yr = pd.to_datetime(filtered_dates.strftime(f'{yr}-%m-%d'))

    filtered_dates_yr = get_initialization_dates(year, **kwargs)

    # Load data using xarray
    ds = xr.open_dataset(file_path)
    if 'time' in ds.dims:
        ds = ds.rename({'time':'init_time'})
    ds = ds.sel(init_time=filtered_dates_yr)
    # Find common dates between desired dates and available dates
    # redundant, len(ds.init_time) or ds.sizes['init_time'] is same as len(matching_times)
    available_init_times = pd.to_datetime(ds.init_time.values)
    matching_times = available_init_times[available_init_times.isin(filtered_dates_yr)]
    if len(matching_times) == 0:
        raise ValueError(f"No matching initialization times found for year {yr}")
    ds = ds.sel(init_time=matching_times)
    # Check if 'day' dimension exists and conditionally slice
    if 'day' in ds.dims:
        # Check if the first value of 'day' is 0, then slice to exclude it
        if ds['day'][0].values == 0:
            ds = ds.sel(day=slice(1, None))
    # Check if 'step' dimension exists and conditionally slice
    if 'step' in ds.dims:
        # Check if the first value of 'step' is 0, then slice to exclude it
        if ds['step'][0].values == 0:
            ds = ds.sel(step=slice(1, None))

    p_model = ds['tp']
    # Only rename 'day' to 'step' if 'day' dimension exists
    if 'day' in p_model.dims:
        p_model = p_model.rename({'day':'step'})

    ds.close()

    return p_model

def get_forecast_probabilistic_twice_weekly(yr, model_forecast_dir, file_pattern='{}.nc',
                                            members=range(1, 31), date_filter_year=2024, **kwargs):
    """
    Loads model precip data for twice-weekly initializations from May to July.
    """
    members = kwargs["members"]
#    date_filter_year = kwargs['date_filter_year']
#    init_days = kwargs["init_days"]
#    start_MMDD = kwargs["start_date"][1:]
#    end_MMDD = kwargs["end_date"][1:]    

    fname = file_pattern.format(yr)
    file_path = os.path.join(model_forecast_dir, fname)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

#    # Filter for twice weekly data from daily for the specified year
#    start_date = datetime(date_filter_year, *start_MMDD)
#    end_date = datetime(date_filter_year, *end_MMDD)
#    date_range = pd.date_range(start_date, end_date, freq='D')
#
#    # Find Mondays and Thursdays
#    # init_days = (0, 3) from config # Monday, Thursday
#    filtered_dates = date_range[date_range.weekday.isin(init_days)]
#    filtered_dates_yr = pd.to_datetime(filtered_dates.strftime(f'{yr}-%m-%d'))

    filtered_dates_yr = get_initialization_dates(year, **kwargs)

    # Load data using xarray
    ds = xr.open_dataset(file_path)
    if 'time' in ds.dims:
        ds = ds.rename({'time': 'init_time'})
    if 'number' in ds.dims:
        ds = ds.rename({'number': 'member'})
    if 'sample' in ds.dims:
        ds = ds.rename({'sample': 'member'})

    # Find common dates between desired dates and available dates
    available_init_times = pd.to_datetime(ds.init_time.values)
    matching_times = available_init_times[available_init_times.isin(filtered_dates_yr)]

    if len(matching_times) == 0:
        raise ValueError(f"No matching initialization times found for year {yr}")

    # Select only the matching initialization times
    ds = ds.sel(init_time=matching_times)
    if "total_precipitation_24hr" in ds.data_vars:
        ds = ds.rename({"total_precipitation_24hr": "tp"}) # For the quantile-mapped variable change the var name from total_precipitation_24hr to tp
        ds = ds[['tp']]*1000  # Convert from m to mm
    if 'day' in ds.dims:
        if ds['day'][0].values == 0:
            ds = ds.sel(day=slice(1, None))

    if 'step' in ds.dims:
        if ds['step'][0].values == 0:
            ds = ds.sel(step=slice(1, None))

    if 'day' in ds.dims:
        ds = ds.rename({'day': 'step'})

    #ds = ds.isel(member =slice(0, mem_num))  # limit to first mem_num members (0-mem_num)
    if members:
        ds = ds.isel(member = members)
    p_model = ds['tp']  # in mm
    init_times = p_model.init_time.values
    ds.close()

    return p_model, init_times


