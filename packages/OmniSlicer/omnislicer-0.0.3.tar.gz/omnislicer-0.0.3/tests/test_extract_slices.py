from OmniSlicer import OmniSlicer

volume_path = "/media/johannes/SSD_2.0TB/ESTRO2026_Survival/data/classification/duschinger/final_dataset/1_Rösner_LMU_Liposarcoma_G2_image.nii.gz"
mask_path = "/media/johannes/SSD_2.0TB/ESTRO2026_Survival/data/classification/duschinger/final_dataset/1_Rösner_LMU_Liposarcoma_G2_label.nii.gz"
output_dir = "./omnislicer_output/"
n_views = 24

OmniSlicer.extract_slices(
    volume_path=volume_path,
    mask_path=mask_path,
    output_dir=output_dir,
    n_views=n_views
)