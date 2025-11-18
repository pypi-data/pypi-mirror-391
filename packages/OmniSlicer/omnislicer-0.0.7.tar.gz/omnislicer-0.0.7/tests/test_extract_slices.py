import sys
sys.path.append("..")
from src.OmniSlicer.OmniSlicer import extract_slices

volume_path = "example_image.nii.gz"
mask_path = "example_mask.nii.gz"
output_dir = "./omnislicer_output/"
n_views = 24

extract_slices(
    volume_path=volume_path,
    mask_path=mask_path,
    output_dir=output_dir,
    n_views=n_views
)
