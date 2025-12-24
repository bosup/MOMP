#from MOMP.io.input import 
from MOMP.lib.loader import cfg, setting
from MOMP.app.bin_skill_score import skill_score_in_bins
from MOMP.app.spatial_far_mr_mae import spatial_far_mr_mae_map

def run_MOMP(cfg=cfg, setting=setting):

    skill_score_in_bins()

    spatial_far_mr_mae_map()

# --------------------------
if __name__ == "__main__":
    # print_momp()
    print("Job starts!")
    run_MOMP()

