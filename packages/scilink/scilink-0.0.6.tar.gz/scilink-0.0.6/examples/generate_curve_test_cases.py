import numpy as np
import os
import logging
import json
import matplotlib.pyplot as plt
from typing import Dict, Any

# Configure basic logging for the test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _gaussian(x, amp, center, sigma):
    """Helper for creating 1D Gaussian peaks."""
    return amp * np.exp(-((x - center)**2) / (2 * sigma**2))

def create_synthetic_curve_data(config: dict):
    """
    Creates a configurable "black box" synthetic 1D curve (N, 2) based on a config dict.
    Returns:
        tuple: (final_data, clean_signal_component)
               Both are (N, 2) numpy arrays.
    """
    n_points = config.get("n_points", 500)
    x_start = config.get("x_start", 0)
    x_end = config.get("x_end", 100)
    
    # --- THIS IS THE MODIFICATION ---
    n_components = config.get("n_components", 2) # Default to 2 peaks
    
    logger.info(f"Creating synthetic curve data ({n_points} points, {n_components} components)...")
    
    np.random.seed(42) # For reproducible noise
    
    # 1. Define X-axis and clean signal
    x = np.linspace(x_start, x_end, n_points)
    
    # Create clean peaks based on n_components
    y_clean = np.zeros_like(x) # Start with zeros
    
    if n_components == 0:
        logger.info("Creating a signal-free dataset (0 components).")
    elif n_components == 1:
        peak_1 = _gaussian(x, amp=1.0, center=30, sigma=3)
        y_clean += peak_1
    else: # Default to 2 peaks
        peak_1 = _gaussian(x, amp=1.0, center=30, sigma=3)
        peak_2 = _gaussian(x, amp=0.7, center=65, sigma=5)
        y_clean = peak_1 + peak_2
    # --- END MODIFICATION ---

    # This is our ground truth
    clean_signal = np.stack([x, y_clean], axis=1)
    
    # Start building the final, corrupted data
    y_final = y_clean.copy()
    
    # 2. Add baseline artifacts (if configured)
    if config.get("add_sloping_baseline", False):
        baseline_level = config.get("baseline_level", 1.5)
        y_baseline = baseline_level * (np.exp(x / (x_end * 1.5)) - 1)
        y_final += y_baseline
        logger.info(f"Added sloping baseline (max level={baseline_level:.2f})")
        
    # 3. Add noise and artifacts (if configured)
    if config.get("add_noise", False):
        noise_level = config.get("noise_level", 0.1)
        y_final += np.random.normal(0, noise_level, n_points)
        logger.info(f"Added Gaussian noise (level={noise_level})")

    if config.get("add_negatives", False):
        neg_region_start = n_points // 10
        neg_region_end = neg_region_start + 50
        y_final[neg_region_start:neg_region_end] -= 0.3
        logger.info(f"Added negative value artifact in region {neg_region_start}-{neg_region_end}")

    final_data = np.stack([x, y_final], axis=1)
    
    return final_data, clean_signal

def _save_ground_truth_plot(final_data: np.ndarray, clean_data: np.ndarray, filename: str, system_info: dict):
    """Saves a plot of the final vs. clean data."""
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(clean_data[:, 0], clean_data[:, 1], 'r--', label="Ground Truth Signal", linewidth=2)
        ax.plot(final_data[:, 0], final_data[:, 1], 'b-', label="Final Corrupted Data", alpha=0.75)
        
        title = system_info.get("title", "Synthetic Curve Data")
        ax.set_title(title)
        ax.set_xlabel("X-axis (a.u.)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.savefig(filename)
        plt.close(fig)
        logger.info(f"Successfully saved ground truth plot to: {filename}")
    except Exception as e:
        logger.error(f"Failed to save ground truth plot: {e}", exc_info=True)


def generate_dataset_and_save(data_config: Dict[str, Any], 
                              system_info: Dict[str, Any], 
                              base_filename: str, 
                              output_dir: str = "curve_test_data"):
    """
    Generates and saves a synthetic dataset based on the provided configs.
    """
    logger.info(f"--- Generating dataset for case: {base_filename} ---")

    # 1. Create data and ground truth
    data, clean_data = create_synthetic_curve_data(data_config)
    
    # 2. Define output filenames and directory
    #    (FIX: Don't create a new subdirectory, just use the one provided)
    os.makedirs(output_dir, exist_ok=True)
    
    data_filename = os.path.join(output_dir, f"{base_filename}_data.npy")
    meta_filename = os.path.join(output_dir, f"{base_filename}_data.json")
    gt_plot_filename = os.path.join(output_dir, f"{base_filename}_ground_truth.png")
    
    # 3. Save the data as .npy
    try:
        np.save(data_filename, data)
        logger.info(f"Successfully saved synthetic data to: {data_filename}")
    except Exception as e:
        logger.error(f"Failed to save data file: {e}", exc_info=True)
        return None  # Return None on failure

    # 4. Save the metadata as .json
    try:
        system_info["title"] = f"Test Case: {base_filename}"
        with open(meta_filename, 'w') as f:
            json.dump(system_info, f, indent=4)
        logger.info(f"Successfully saved metadata to: {meta_filename}")
    except Exception as e:
        logger.error(f"Failed to save metadata file: {e}", exc_info=True)
        return None  # Return None on failure
    
    # 5. Save the ground truth plot
    _save_ground_truth_plot(data, clean_data, gt_plot_filename, system_info)
        
    print(f"Successfully created files for case '{base_filename}' in '{output_dir}' directory.")
    print(f"  Data: {data_filename}")
    print(f"  Meta: {meta_filename}\n")
    
    return {
        "data_file": data_filename,
        "meta_file": meta_filename,
        "plot_file": gt_plot_filename
    }

def get_default_system_info() -> Dict[str, Any]:
    """Returns the base system_info dictionary."""
    return {
        "experiment_type": "1D Spectroscopy",
        "experiment": {"technique": "Raman Spectrum"},
        "sample": {"material": "Test Sample"},
    }

def get_test_case_configs() -> Dict[str, Dict[str, Any]]:
    """Returns a dictionary of predefined test cases for the agent."""
    
    base_config = {
        "n_points": 500, "x_start": 0, "x_end": 100,
        "n_components": 2, # <-- ADDED
        "add_sloping_baseline": False, "baseline_level": 1.5,
        "add_noise": False, "noise_level": 0.1,
        "add_negatives": False,
    }
    
    generic_system_info = get_default_system_info()
    test_cases = {}
    
    # --- Test Case 1: Standard Path (Noise + Negatives) ---
    # Tests the default "smart" strategy (clip + smooth)
    
    standard_config = base_config.copy()
    standard_config.update({
        "add_noise": True,
        "noise_level": 0.08,
        "add_negatives": True,
    })
    test_cases["standard_processing"] = {
        "data_config": standard_config,
        "system_info": generic_system_info.copy()
    }

    # --- Test Case 2: Custom Script Path (Success) ---
    # Tests a solvable custom instruction
    
    custom_config_success = base_config.copy()
    custom_config_success.update({
        "add_sloping_baseline": True,
        "baseline_level": 2.0,
        "add_noise": True,
        "noise_level": 0.03,
    })
    
    custom_system_info_success = generic_system_info.copy()
    custom_system_info_success["custom_processing_instruction"] = (
        "This data has a strong sloping baseline that is hiding the peaks. "
        "Please use a robust method like Asymmetric Least Squares (ALS) or a "
        "polynomial fit from scipy or sklearn to remove this baseline."
    )

    test_cases["custom_processing_success"] = {
        "data_config": custom_config_success,
        "system_info": custom_system_info_success
    }
    
    # --- Test Case 3: Custom Script Path (Failure Loop) ---
    # This test provides data with NO peaks and tells the agent to find them.
    # This should fail the quality validation loop.
    
    custom_config_fail = base_config.copy()
    custom_config_fail.update({
        "n_components": 0, # <-- NO PEAKS
        "add_sloping_baseline": True,
        "baseline_level": 1.0,
        "add_noise": True,
        "noise_level": 0.1,
    })
    
    custom_system_info_fail = generic_system_info.copy()
    custom_system_info_fail["custom_processing_instruction"] = (
        "This data clearly shows two main Gaussian peaks on a sloping baseline. "
        "Your task is to remove the baseline and perfectly isolate the two peaks. "
        "The peaks are the most important part."
    )

    test_cases["custom_processing_fail"] = {
        "data_config": custom_config_fail,
        "system_info": custom_system_info_fail
    }
    
    return test_cases

def main():
    """
    Generates all test cases defined in the config.
    """
    all_cases = get_test_case_configs()
    
    for case_name, configs in all_cases.items():
        generate_dataset_and_save(
            data_config=configs["data_config"],
            system_info=configs["system_info"],
            base_filename=case_name,
            output_dir="curve_test_data"
        )
    
    logger.info("\nAll test cases generated successfully.")

if __name__ == "__main__":
    main()