import numpy as np
import os
import logging
import json
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Tuple

# Configure basic logging for the test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _gaussian(x, amp, center, sigma):
    """Helper for creating 1D Gaussian spectra."""
    return amp * np.exp(-((x - center)**2) / (2 * sigma**2))

def _gaussian_2d(x, y, amp, center_x, center_y, sigma_x, sigma_y):
    """Helper for creating 2D Gaussian spatial maps."""
    return amp * np.exp(
        -(((x - center_x)**2 / (2 * sigma_x**2)) + 
          ((y - center_y)**2 / (2 * sigma_y**2)))
    )
    
def create_synthetic_data(config: dict):
    """
    Creates a configurable "black box" synthetic 3D dataset based on a config dict.
    """
    h = config.get("h", 100)
    w = config.get("w", 100)
    e = config.get("e", 256)
    n_components = config.get("n_components", 3)
    
    # Get substrate_level from config, defaulting to 0.1
    substrate_level = config.get("substrate_level", 0.1)

    logger.info(f"Creating synthetic data ({h}x{w}x{e}) with {n_components} components...")
    
    np.random.seed(42) # For reproducible noise
    
    # 1. Define spectral components
    spec_channels = np.arange(e)
    spec_A = _gaussian(spec_channels, amp=1.0, center=e*0.25, sigma=e*0.05)
    spec_I = _gaussian(spec_channels, amp=1.2, center=e*0.50, sigma=e*0.10)
    spec_B = _gaussian(spec_channels, amp=0.8, center=e*0.75, sigma=e*0.05)
    spec_unused = _gaussian(spec_channels, amp=0.5, center=e*0.80, sigma=e*0.04)
    all_spectra = [spec_A, spec_I, spec_B, spec_unused]

    # 2. Define spatial maps
    y, x = np.indices((h, w))
    min_signal_level = 0.2 
    max_signal_level = 1.0
    signal_range = max_signal_level - min_signal_level
    map_A_mask = np.zeros((h, w)); map_A_mask[:, :45] = 1.0
    map_B_mask = np.zeros((h, w)); map_B_mask[:, 55:] = 1.0
    gradient_A = (44 - x) / 44 
    map_A_gradient = min_signal_level + (signal_range * gradient_A)
    map_A = map_A_gradient * map_A_mask
    map_I = _gaussian_2d(x, y, amp=1.5, center_x=50, center_y=h/2, sigma_x=4, sigma_y=h*2)
    gradient_B = (x - 55) / (w - 1 - 55)
    map_B_gradient = min_signal_level + (signal_range * gradient_B)
    map_B = map_B_gradient * map_B_mask
    map_unused = np.ones((h, w)) * 0.1
    all_maps = [map_A, map_I, map_B, map_unused]
    
    if n_components > len(all_spectra):
        raise ValueError(f"Config n_components ({n_components}) is larger than pre-defined components ({len(all_spectra)})")

    spectra_to_plot = all_spectra[:n_components]
    maps_to_plot = all_maps[:n_components]

    # 3. Create clean data by combining components
    
    # Only add substrate if its level is > 0
    if substrate_level > 1e-9:
        spec_substrate = np.ones(e) # A simple flat spectrum for the substrate
        clean_data = np.full((h, w, e), substrate_level) * spec_substrate
        logger.info(f"Applying substrate with level {substrate_level}")
    else:
        clean_data = np.zeros((h, w, e))
        logger.info("No substrate applied (level is zero).")

    for i in range(n_components):
        clean_data += maps_to_plot[i][..., np.newaxis] * spectra_to_plot[i]
    
    data = clean_data
    
    # 4. Add noise based on config
    if config.get("add_background_noise", True):
        level = config.get("background_level", 0.1)
        data += np.random.rand(h, w, e) * level
        logger.info(f"Added background noise (level={level})")

    if config.get("add_gaussian_noise", True):
        level = config.get("gaussian_level", 0.05)
        data += np.random.normal(0, level, (h, w, e))
        logger.info(f"Added Gaussian noise (level={level})")
    
    if config.get("add_negative_noise", True):
        level = config.get("negative_level", -0.5)
        data[10:20, 10:20, :] = level + np.random.normal(0, 0.05, (10, 10, e))
        logger.info(f"Added negative noise region (level={level})")

    if config.get("add_spikes", True):
        spike_mode = config.get("spike_mode", "random")
        
        if spike_mode == "correlated":
            # ... (no changes to this block) ...
            n_spike_events = config.get("n_spike_events", 10)
            pixels_per_event = config.get("pixels_per_event", 5)
            intensity = config.get("spike_intensity", 1500.0)
            spatial_clustering = config.get("spike_spatial_clustering", False)
            energy_clustering = config.get("spike_energy_clustering", False)
            energy_cluster_width = config.get("spike_energy_cluster_width", 10)
            
            total_spikes = 0
            affected_energies = []
            
            if energy_clustering:
                center_energy = np.random.randint(energy_cluster_width, e - energy_cluster_width)
                logger.info(f"Energy clustering enabled: spikes centered around channel {center_energy}")
                spike_energies = []
                for event in range(n_spike_events):
                    offset = int(np.random.normal(0, energy_cluster_width / 3))
                    spike_energy = np.clip(center_energy + offset, 0, e - 1)
                    spike_energies.append(spike_energy)
            else:
                spike_energies = [np.random.randint(0, e) for _ in range(n_spike_events)]
            
            affected_energies = spike_energies
            
            for event, spike_energy in enumerate(spike_energies):
                if spatial_clustering:
                    center_h = np.random.randint(10, h - 10)
                    center_w = np.random.randint(10, w - 10)
                    for _ in range(pixels_per_event):
                        offset_h = int(np.random.normal(0, 5))
                        offset_w = int(np.random.normal(0, 5))
                        spike_h = np.clip(center_h + offset_h, 0, h - 1)
                        spike_w = np.clip(center_w + offset_w, 0, w - 1)
                        spike_value = np.random.uniform(intensity * 0.8, intensity * 1.2)
                        data[spike_h, spike_w, spike_energy] = spike_value
                        total_spikes += 1
                else:
                    for _ in range(pixels_per_event):
                        spike_h = np.random.randint(0, h)
                        spike_w = np.random.randint(0, w)
                        spike_value = np.random.uniform(intensity * 0.8, intensity * 1.2)
                        data[spike_h, spike_w, spike_energy] = spike_value
                        total_spikes += 1
            
            logger.info(f"Added {total_spikes} correlated spikes across {n_spike_events} energy channels")
            if len(affected_energies) <= 10:
                logger.info(f"  Affected energy channels: {sorted(affected_energies)}")
            else:
                logger.info(f"  Affected energy channels (first 10): {sorted(affected_energies)[:10]}...")
            logger.info(f"  Energy clustering: {energy_clustering} (width={energy_cluster_width if energy_clustering else 'N/A'})")
            logger.info(f"  Spatial clustering: {spatial_clustering}")
            
        else:
            # Original random spike mode
            n_spikes = config.get("n_spikes", 50)
            intensity = config.get("spike_intensity", 1500.0)
            for _ in range(n_spikes):
                spike_h = np.random.randint(0, h)
                spike_w = np.random.randint(0, w)
                spike_e = np.random.randint(0, e)
                data[spike_h, spike_w, spike_e] = np.random.uniform(intensity, intensity + 200.0)
            logger.info(f"Added {n_spikes} random spikes (intensity ~{intensity})")
    
    # <-- NEW BLOCK START -->
    # 5. Add "Hot Pixels" (bad detector pixels)
    if config.get("add_hot_pixels", False):
        hot_pixel_list = config.get("hot_pixel_coords", [])
        intensity = config.get("hot_pixel_intensity", 25.0) # A high, constant value
        if hot_pixel_list:
            logger.info(f"Adding {len(hot_pixel_list)} hot pixels...")
            for (h_coord, w_coord) in hot_pixel_list:
                if 0 <= h_coord < h and 0 <= w_coord < w:
                    # Replace the *entire* spectrum at this pixel with a high constant value
                    data[h_coord, w_coord, :] = intensity + np.random.rand(e) * intensity * 0.05
                    logger.info(f"  ... added hot pixel at ({h_coord}, {w_coord}) with intensity {intensity}")
                else:
                    logger.warning(f"  ... hot pixel coord ({h_coord}, {w_coord}) is out of bounds. Skipping.")
    # <-- NEW BLOCK END -->

    logger.info(f"Realistic synthetic data created: Min={np.min(data):.2f}, Max={np.max(data):.2f}, Mean={np.mean(data):.2f}")
    return data, spectra_to_plot, maps_to_plot

def _save_ground_truth_plot(spectra: list, maps: list, filename: str, energy_range: dict = None):
    # ... (no changes to this function) ...
    try:
        n_components = len(spectra)
        if n_components == 0:
            logger.warning("No ground truth components to plot.")
            return

        fig, axes = plt.subplots(2, n_components, figsize=(n_components * 4.5, 8), squeeze=False)
        fig.suptitle("Ground Truth Synthetic Components (Clean)", fontsize=16)

        e = spectra[0].shape[0]
        x_axis = np.arange(e)
        x_label = f"Channel (0-{e-1})"
        
        if n_components == 3:
            spec_titles = ["Phase A (Spectrum)", "Interface (Spectrum)", "Phase B (Spectrum)"]
            map_titles = ["Phase A Map (Gradient)", "Interface Map", "Phase B Map (Gradient)"]
        else:
            spec_titles = [f"Ground Truth Spectrum {i+1}" for i in range(n_components)]
            map_titles = [f"Ground Truth Map {i+1}" for i in range(n_components)]
            
        if energy_range:
            start = energy_range.get("start", 0)
            end = energy_range.get("end", e-1)
            units = energy_range.get("units", "a.u.")
            x_axis = np.linspace(start, end, e)
            x_label = f"Energy ({units})"
        
        for i in range(n_components):
            ax_spec = axes[0, i]
            ax_spec.plot(x_axis, spectra[i], label=f"GT Comp {i+1}")
            ax_spec.set_title(spec_titles[i])
            ax_spec.set_xlabel(x_label)
            ax_spec.set_ylabel("Intensity (a.u.)")
            ax_spec.grid(True, alpha=0.3)
            
            ax_map = axes[1, i]
            im = ax_map.imshow(maps[i], aspect='auto')
            ax_map.set_title(map_titles[i])
            ax_map.axis('off')
            plt.colorbar(im, ax=ax_map, fraction=0.046, pad=0.04)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(filename)
        plt.close(fig)
        logger.info(f"Successfully saved ground truth plot to: {filename}")
    except Exception as e:
        logger.error(f"Failed to save ground truth plot: {e}", exc_info=True)


def convert_sets_to_lists(obj):
    # ... (no changes to this function) ...
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_sets_to_lists(element) for element in obj]
    return obj

# --- NEW REUSABLE FUNCTIONS ---

def generate_dataset_and_save(data_config: Dict[str, Any], 
                              system_info: Dict[str, Any], 
                              base_filename: str, 
                              output_dir: str = "data") -> Dict[str, str]:
    # ... (no changes to this function) ...
    logger.info(f"--- Generating dataset for case: {base_filename} ---")

    # 1. Create data and ground truth components
    data, gt_spectra, gt_maps = create_synthetic_data(data_config)
    
    # 2. Define output filenames and directory
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
        return {}

    # 4. Save the metadata as .json
    try:
        # Use the passed-in system_info directly
        cleaned_system_info = convert_sets_to_lists(system_info)
        with open(meta_filename, 'w') as f:
            json.dump(cleaned_system_info, f, indent=4)
        logger.info(f"Successfully saved metadata to: {meta_filename}")
    except Exception as e:
        logger.error(f"Failed to save metadata file: {e}", exc_info=True)
        return {}
    
    # 5. Save the ground truth plot
    try:
        _save_ground_truth_plot(gt_spectra, gt_maps, gt_plot_filename, system_info.get("energy_range"))
    except Exception as e:
        logger.error(f"Failed to save ground truth plot: {e}", exc_info=True)
        
    print(f"\nSuccessfully created files for case '{base_filename}' in '{output_dir}' directory.")
    
    # Return the file paths for the notebook to use
    return {
        "data_file": data_filename,
        "meta_file": meta_filename,
        "plot_file": gt_plot_filename
    }

def get_default_system_info() -> Dict[str, Any]:
    # ... (no changes to this function) ...
    return {
        "experiment_type": "Spectroscopy",
        "experiment": {"technique": "Raman Map"},
        "sample": {"material": "Heterostructure"}, # <-- Generic description
        "energy_range": {
            "start": 100,
            "end": 800,
            "units": "cm^-1",
        }
    }

def get_test_case_configs() -> Dict[str, Dict[str, Any]]:
    """Returns a dictionary of predefined test cases for the agent."""
    
    base_config = {
        "h": 100, "w": 100, "e": 256, "n_components": 3,
        "substrate_level": 0.1,
        "add_background_noise": False, "background_level": 0.1,
        "add_gaussian_noise": False, "gaussian_level": 0.05,
        "add_negative_noise": False, "negative_level": -0.5,
        "add_spikes": False, "n_spikes": 50, "spike_intensity": 1500.0,
        "add_hot_pixels": False, "hot_pixel_coords": [], "hot_pixel_intensity": 25.0 # <-- Add hot_pixel defaults
    }
    
    generic_system_info = get_default_system_info()
    test_cases = {}
    
    # 1. Clean substrate (baseline - no corruption)
    # ... (no change)
    test_cases["clean_substrate"] = {
        "data_config": base_config.copy(),
        "system_info": generic_system_info.copy()
    }

    # # 2. Random spikes (original, simplest case)
    # # ... (no change)
    # cosmic_ray_random = base_config.copy()
    # cosmic_ray_random.update({
    #     "add_spikes": True,
    #     "spike_mode": "random",
    #     "n_spikes": 50,
    #     "spike_intensity": 1500.0
    # })
    # test_cases["cosmic_ray_random"] = {
    #     "data_config": cosmic_ray_random,
    #     "system_info": generic_system_info.copy()
    # }

    # # 3. Correlated spikes - Energy correlation ONLY
    # # ... (no change)
    # cosmic_ray_correlated = base_config.copy()
    # cosmic_ray_correlated.update({
    #     "add_spikes": True,
    #     "spike_mode": "correlated",
    #     "n_spike_events": 10,
    #     "pixels_per_event": 5,
    #     "spike_intensity": 1500.0,
    #     "spike_spatial_clustering": False,
    #     "spike_energy_clustering": False
    # })
    # test_cases["cosmic_ray_correlated"] = {
    #     "data_config": cosmic_ray_correlated,
    #     "system_info": generic_system_info.copy()
    # }

    # 4. ULTIMATE TEST: Both energy AND spatial clustering
    spike_nightmare = base_config.copy()
    spike_nightmare.update({
        "add_spikes": True,
        "spike_mode": "correlated",
        "n_spike_events": 8,
        "pixels_per_event": 6,
        "spike_intensity": 1800.0,
        "spike_spatial_clustering": True,
        "spike_energy_clustering": True,
        "spike_energy_cluster_width": 10
    })
    test_cases["spike_nightmare"] = {
        "data_config": spike_nightmare,
        "system_info": generic_system_info.copy()
    }

    # 5. Noisy Background (masking test)
    noisy_bg_config = base_config.copy()
    noisy_bg_config.update({
        "substrate_level": 0.0,
        "add_gaussian_noise": True,
        "gaussian_level": 0.05
    })
    test_cases["noisy_background"] = {
        "data_config": noisy_bg_config,
        "system_info": generic_system_info.copy()
    }
    
    # 6. Negative Artifact (clipping test)
    negative_config = base_config.copy()
    negative_config.update({
        "add_negative_noise": True,
        "negative_level": -0.5
    })
    test_cases["negative_artifact"] = {
        "data_config": negative_config,
        "system_info": generic_system_info.copy()
    }
    
    # 7. Custom Script Test (Hot Pixel Removal)
    hot_pixel_config = base_config.copy()
    hot_pixel_config.update({
        "add_hot_pixels": True,
        "hot_pixel_coords": [(25, 75), (50, 50)], # Add two hot pixels
        "hot_pixel_intensity": 25.0
    })
    
    hot_pixel_system_info = generic_system_info.copy()
    
    hot_pixel_system_info["custom_processing_instruction"] = (
        "This dataset contains several known 'hot pixels' (bad detectors) that "
        "are stuck at a high value across all energy channels. "
        "Please write a script to correct this. For each pixel, if the pixel's "
        "median intensity is 5x greater than the global median, replace its "
        "entire spectrum with the spatial median spectrum of its 3x3 neighborhood."
    )

    test_cases["custom_hot_pixel_removal"] = {
        "data_config": hot_pixel_config,
        "system_info": hot_pixel_system_info
    }
    
    return test_cases

def main():
    """
    Runs the *default* test case ("clean_substrate")
    when the script is executed directly.
    """
    all_cases = get_test_case_configs()
    default_case = all_cases["clean_substrate"]
    
    generate_dataset_and_save(
        data_config=default_case["data_config"],
        system_info=default_case["system_info"],
        base_filename="synthetic_default", # A new default name
        output_dir="data" # Default save location
    )

if __name__ == "__main__":
    main()