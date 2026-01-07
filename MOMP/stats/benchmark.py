from MOMP.io.input import load_thresh_file, get_initialization_dates
from MOMP.io.input import get_forecast_probabilistic_twice_weekly, get_forecast_deterministic_twice_weekly
from MOMP.io.input import load_imd_rainfall
from MOMP.stats.detect import detect_observed_onset, compute_onset_for_deterministic_model, compute_onset_for_all_members
from MOMP.stats.climatology import compute_climatological_onset, compute_climatology_as_forecast


def compute_onset_metrics_with_windows(onset_df, tolerance_days=3, verification_window=(1,15), **kwargs):
    """Compute contingency matrix metrics following MATLAB logic with forecast and validation windows."""
    print(f"Computing onset metrics with tolerance = {tolerance_days} days")
    print(f"Verification window starts {verification_window} days after initialization")
    print(f"Forecast window length: {verification_window[1]} days")

    #forecast_bin_start = kwargs["forecast_bin"][0]
    #forecast_bin_end = kwargs["forecast_bin"][1]
    forecast_bin_start = verification_window[0]
    forecast_bin_end = verification_window[1]

    results_list = []
    unique_locations = onset_df[['lat', 'lon']].drop_duplicates()

    print(f"Processing {len(unique_locations)} unique grid points...")

    for idx, (_, row) in enumerate(unique_locations.iterrows()):
        lat, lon = row['lat'], row['lon']

        if idx % 10 == 0:
            print(f"Processing grid point {idx+1}/{len(unique_locations)}: lat={lat:.2f}, lon={lon:.2f}")

        grid_data = onset_df[(onset_df['lat'] == lat) & (onset_df['lon'] == lon)].copy()

        grid_data['obs_onset_dt'] = pd.to_datetime(grid_data['obs_onset_date'])
        grid_data['model_onset_dt'] = pd.to_datetime(grid_data['onset_date'])
        grid_data['init_dt'] = pd.to_datetime(grid_data['init_time'])

        TP = 0
        FP = 0
        FN = 0
        TN = 0
        num_onset = 0
        num_no_onset = 0
        mae_tp = []
        mae_fp = []

        gt_grd = grid_data['obs_onset_dt'].iloc[0]

        #true_onset_window_start = gt_grd - pd.Timedelta(days=tolerance_days)
        #true_onset_window_end = gt_grd + pd.Timedelta(days=tolerance_days)

        for _, init_row in grid_data.iterrows():
            t_init = init_row['init_dt']
            model_onset = init_row['model_onset_dt']

            valid_window_start = t_init + pd.Timedelta(days=forecast_bin_start)
            valid_window_end = valid_window_start + pd.Timedelta(days=forecast_bin_end - 1)

            whole_forecast_window_start = t_init + pd.Timedelta(days=1)
            whole_forecast_window_end = t_init + pd.Timedelta(days=forecast_bin_end)

#            # Double-check: Only use forecasts initialized before the observed onset
#            if init_date >= obs_date_dt:
#                continue

            is_onset_in_whole_window = whole_forecast_window_start <= gt_grd <= whole_forecast_window_end

            if is_onset_in_whole_window:
                num_onset += 1
            else:
                num_no_onset += 1

#            # for 16-30 days, make sure no model onset occur before for day 1-15
#            if verification_window == 1:
#                has_model_onset = not pd.isna(model_onset)
#            else:
#                early_onset = 1 <= model_onset <= valid_window_start
#                has_model_onset = not pd.isna(model_onset) and not early_onset

            has_model_onset = not pd.isna(model_onset)

            if has_model_onset:
                is_model_in_valid_window = valid_window_start <= model_onset <= valid_window_end

                if is_model_in_valid_window:
                    abs_diff_days = abs((model_onset - gt_grd).days)

                    if abs_diff_days <= tolerance_days:
                        TP += 1
                        mae_tp.append(abs_diff_days)
                    else:
                        FP += 1
                        mae_fp.append(abs_diff_days)

                else:
                    if model_onset > valid_window_end: #make sure no model onset in early bins
                        if is_onset_in_whole_window:
                            FN += 1
                        else:
                            TN += 1

            else:
                if is_onset_in_whole_window:
                    FN += 1
                else:
                    TN += 1

        total_forecasts = len(grid_data)

        mae_combined = mae_tp + mae_fp
        mae = np.mean(mae_combined) if len(mae_combined) > 0 else np.nan
        mae_tp_only = np.mean(mae_tp) if len(mae_tp) > 0 else np.nan

        result = {
            'lat': lat,
            'lon': lon,
            'total_forecasts': total_forecasts,
            'true_positive': TP,
            'true_negative': TN,
            'false_positive': FP,
            'false_negative': FN,
            'num_onset': num_onset,
            'num_no_onset': num_no_onset,
            'mae_combined': mae,
            'mae_tp_only': mae_tp_only,
            'num_tp_errors': len(mae_tp),
            'num_fp_errors': len(mae_fp),
            'tolerance_days': tolerance_days,
            'verification_window': verification_window, #forecast_bin,
            'forecast_days': forecast_bin_end
        }
        results_list.append(result)

    metrics_df = pd.DataFrame(results_list)

    summary_stats = {
        'total_grid_points': len(metrics_df),
        'total_forecasts': metrics_df['total_forecasts'].sum(),
        'overall_true_positive': metrics_df['true_positive'].sum(),
        'overall_true_negative': metrics_df['true_negative'].sum(),
        'overall_false_positive': metrics_df['false_positive'].sum(),
        'overall_false_negative': metrics_df['false_negative'].sum(),
        'overall_num_onset': metrics_df['num_onset'].sum(),
        'overall_num_no_onset': metrics_df['num_no_onset'].sum(),
        'overall_mae_combined': metrics_df['mae_combined'].mean(),
        'overall_mae_tp_only': metrics_df['mae_tp_only'].mean(),
        'tolerance_days': tolerance_days,
        'verification_window': verification_window,
        'forecast_days': forecast_bin_end
    }

    return metrics_df, summary_stats



def compute_metrics_multiple_years(years, *, model_dir, obs_dir, thresh_file, file_pattern,
                                 tolerance_days, verification_window,
                                 mok, members, climatology, probabilistic, **kwargs):
    """Compute onset metrics for multiple years."""
#
    #members = kwargs['members']
    #probabilistic = kwargs['probabilistic']

    #mok = kwargs["mok"]
    #window = kwargs["wet_spell"]
    #wet_init = kwargs["wet_init"]
    #dry_spell = kwargs["dry_spell"]
    #dry_extent = kwargs["dry_extent"]
    #dry_threshold = kwargs["dry_threshold"]
    #max_forecast_day = kwargs['max_forecast_day']
    #tolerance_days = kwargs['tolerance_days']
    #verification_window = kwargs['verification_window']

    #climatology = kwargs['climatology']

    #forecast_bin_start = verification_window[0]
    #forecast_bin_end = verification_window[1]


    metrics_df_dict = {}
    onset_da_dict = {}
#
    # depend on if thresh is a 2-D array or scalar
    thresh_da = load_thresh_file(**kwargs)

    if climatology:
        climatological_onset_doy = compute_climatological_onset(obs_dir, thresh_file, mok=mok)

    for year in years:
        print(f"\n{'='*50}")
        print(f"Processing year {year}")
        print(f"{'='*50}")

        imd = load_imd_rainfall(year, **kwargs)

        onset_da = detect_observed_onset(imd, thresh_da, year, mok=mok, **kwargs)

        if probabilistic:
            p_model = get_forecast_probabilistic_twice_weekly(year, model_forecast_dir, file_pattern, members, **kwargs)
        elif not climatology:
            p_model = get_forecast_deterministic_twice_weekly(year, model_forecast_dir, file_pattern, **kwargs)


        if probabilistic:
            _, onset_df = compute_onset_for_all_members(
                p_model, thresh_da, onset_da, **kwargs
            )

        elif not climatology:
            onset_df = compute_onset_for_deterministic_model(
                p_model, thresh_da, onset_da,
                max_forecast_day=max_forecast_day, mok=mok, **kwargs
            )

        elif climatology:
            init_dates = get_initialization_dates(year)
            onset_df = compute_climatology_as_forecast(
                climatological_onset_doy, year, init_dates, onset_da,
                max_forecast_day=max_forecast_day, mok=mok
            )


        metrics_df, summary_stats = compute_onset_metrics_with_windows(
            onset_df,
            tolerance_days=tolerance_days,
            verification_window=verification_window, **kwargs
        )

        metrics_df_dict[year] = metrics_df

        if not climatology:
            onset_da_dict[year] = onset_da

        print(f"Year {year} completed. Grid points processed: {len(metrics_df)}")
        print(f"Summary stats: TP={summary_stats['overall_true_positive']}, "
              f"FP={summary_stats['overall_false_positive']}, "
              f"FN={summary_stats['overall_false_negative']}, "
              f"TN={summary_stats['overall_true_negative']}")

    if climatology:
        onset_da_dict = {year: climatological_onset_doy for year in years}

    return metrics_df_dict, onset_da_dict


