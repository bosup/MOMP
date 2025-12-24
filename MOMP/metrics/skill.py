from MOMP.io.input import load_thresh_file, get_initialization_dates
from MOMP.io.input import get_forecast_probabilistic_twice_weekly, get_forecast_deterministic_twice_weekly
from MOMP.io.input import load_imd_rainfall
#from MOMP.io.output import save_score_results
from MOMP.stats.detect import detect_observed_onset, compute_onset_for_all_members
from MOMP.stats.climatology import compute_climatological_onset_dataset
from MOMP.stats.bins import get_target_bins, create_forecast_observation_pairs_with_bins, create_climatological_forecast_obs_pairs, multi_year_forecast_obs_pairs, multi_year_climatological_forecast_obs_pairs
from MOMP.stats.score import calculate_brier_score, calculate_auc, calculate_rps, calculate_brier_score_climatology, calculate_auc_climatology, calculate_skill_scores

def create_score_results(BSS, RPS, AUC, skill_score, ref_model, ref_model_dir,
                         years, years_clim, model, model_forecast_dir, imd_folder, thres_file
                         members, max_forecast_day, day_bins, date_filter_year,
                         file_pattern, mok, **kwargs):

#    print("="*60)
#    print("S2S MONSOON ONSET SKILL SCORE ANALYSIS")
#    print("="*60)
#    print(f"Model: {model}")
#    print(f"Years: {years}")
#    print(f"Max forecast day: {max_forecast_day}")
#    print(f"Day bins: {day_bins}")
#    print(f"MOK filter: {mok}")
#    print("="*60)

    results = {}

    print("\n1. Processing forecast model...")
    forecast_obs_df = multi_year_forecast_obs_pairs(**kwargs)
    results["forecast_obs_df"] = forecast_obs_df

    results["BSS"] = calculate_brier_score(forecast_obs_df) if BSS else None
    results["RPS"] = calculate_rps(forecast_obs_df) if RPS else None
    results["AUC"] = calculate_auc(forecast_obs_df) if AUC else None


    print("\n1. Processing reference model...")

    results["BSS_ref"], results["RPS_ref"], results["AUC_ref"] = None, None, None
    results['skill_score'] = None

    if ref_model == "climatology":

        clim_onset = compute_climatological_onset_dataset(**kwargs)
        climatology_obs_df = multi_year_climatological_forecast_obs_pairs(**kwargs)
        results["climatology_obs_df"] = climatology_obs_df
        
        if BSS:
            brier_ref = calculate_brier_score_climatology(climatology_obs_df)
            results["BSS_ref"] = brier_ref
        
        if RPS:
            rps_ref = calculate_rps(climatology_obs_df)
            results["RPS_ref"] = rps_ref

        if AUC:
            auc_ref = calculate_auc_climatology(climatology_obs_df)
            results["AUC_ref"] = auc_ref

    else:
        kwargs_ref = {**kwargs, 'model_forecast_dir': ref_model_dir}
        ref_obs_df = multi_year_forecast_obs_pairs(**kwargs_ref)

        if BSS:
            brier_ref = calculate_brier_score(ref_obs_df)
            results["BSS_ref"] = brier_ref
        
        if RPS:
            rps_ref = calculate_rps(ref_obs_df)
            results["RPS_ref"] = rps_ref

        if AUC:
            auc_ref = calculate_auc(ref_obs_df)
            results["AUC_ref"] = auc_ref


    if skill_score:

        skill_results = calculate_skill_scores(
        brier_forecast, rps_forecast,
        brier_ref, rps_ref
        )

        results["skill_results"] = skill_results

#    if save_csv_score:
#        save_score_results(results, model, max_forecast_day))


    return results

