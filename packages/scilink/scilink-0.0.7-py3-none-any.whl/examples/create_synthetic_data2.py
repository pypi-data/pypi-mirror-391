import numpy as np
import os
import logging
import json
import matplotlib.pyplot as plt

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
    
    Returns:
        tuple: (
            noisy_data (np.ndarray), 
            spectra_to_plot (list[np.ndarray]), 
            maps_to_plot (list[np.ndarray])
        )
    """
    h = config.get("h", 100)
    w = config.get("w", 100)
    e = config.get("e", 256)
    n_components = config.get("n_components", 3)
    
    # --- THIS IS THE FIX ---
    # Add a constant, low-level "substrate" signal everywhere
    # This will be our new "minimum" and will raise the P50 (median)
    substrate_level = 0.1
    # --- END FIX ---

    logger.info(f"Creating synthetic data ({h}x{w}x{e}) with {n_components} components...")
    
    np.random.seed(42) # For reproducible noise
    
    # 1. Define spectral components
    spec_channels = np.arange(e)
    spec_A = _gaussian(spec_channels, amp=1.0, center=e*0.25, sigma=e*0.05)
    spec_I = _gaussian(spec_channels, amp=1.2, center=e*0.50, sigma=e*0.10)
    spec_B = _gaussian(spec_channels, amp=0.8, center=e*0.75, sigma=e*0.05)
    spec_unused = _gaussian(spec_channels, amp=0.5, center=e*0.80, sigma=e*0.04)
    all_spectra = [spec_A, spec_I, spec_B, spec_unused]

    # 2. Define spatial maps (with gradients away from interface)
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
    
    # --- THIS IS THE OTHER PART OF THE FIX ---
    # Start with a base substrate signal, not zeros.
    spec_substrate = np.ones(e) # A simple flat spectrum for the substrate
    clean_data = np.full((h, w, e), substrate_level) * spec_substrate
    # --- END FIX ---

    for i in range(n_components):
        clean_data += maps_to_plot[i][..., np.newaxis] * spectra_to_plot[i]
    
    data = clean_data
    
    # 4. Add noise based on config
    
    if config.get("add_background_noise", True):
        level = config.get("background_level", 0.1)
        background_noise = np.random.rand(h, w, e) * level
        data += background_noise
        logger.info(f"Added background noise (level={level})")

    if config.get("add_gaussian_noise", True):
        level = config.get("gaussian_level", 0.05)
        gaussian_noise = np.random.normal(0, level, (h, w, e))
        data += gaussian_noise
        logger.info(f"Added Gaussian noise (level={level})")
    
    # --- MOVED THESE FROM THE DELETED FUNCTION ---
    # 5. Add negative noise
    if config.get("add_negative_noise", True):
        level = config.get("negative_level", -0.5)
        data[10:20, 10:20, :] = level + np.random.normal(0, 0.05, (10, 10, e))
        logger.info(f"Added negative noise region (level={level})")

    # 6. Add spikes
    # if config.get("add_spikes", True):
    #     n_spikes = config.get("n_spikes", 10)
    #     intensity = config.get("spike_intensity", 800.0)
    #     for _ in range(n_spikes):
    #         spike_h, spike_w, spike_e = np.random.randint(0, h), np.random.randint(0, w), np.random.randint(0, e)
    #         data[spike_h, spike_w, spike_e] = np.random.uniform(intensity, intensity + 200.0)
    #     logger.info(f"Added {n_spikes} spikes (intensity ~{intensity})")
    if config.get("add_spikes", True):
        n_spike_events = config.get("n_spike_events", 5)  # Number of "cosmic ray events"
        pixels_per_event = config.get("pixels_per_event", 3)  # Pixels affected per event
        intensity = config.get("spike_intensity", 800.0)
        
        logger.info(f"Adding {n_spike_events} spike events, each affecting ~{pixels_per_event} pixels...")
        
        for event in range(n_spike_events):
            # Each "event" affects the SAME energy channel in multiple pixels
            spike_energy = np.random.randint(0, e)  # Pick ONE energy for this event
            
            # Affect multiple nearby pixels (simulates detector artifact spreading)
            for _ in range(pixels_per_event):
                spike_h = np.random.randint(0, h)
                spike_w = np.random.randint(0, w)
                
                # All spikes in this event have SAME energy, similar intensity
                spike_value = np.random.uniform(intensity * 0.8, intensity * 1.2)
                data[spike_h, spike_w, spike_energy] = spike_value
                
                logger.debug(f"  Event {event+1}: spike at ({spike_h}, {spike_w}, E={spike_energy}) = {spike_value:.1f}")
        
        logger.info(f"Added {n_spike_events * pixels_per_event} total spike pixels across {n_spike_events} energy channels")
    # --- END MOVED BLOCKS ---
    
    logger.info(f"Realistic synthetic data created: Min={np.min(data):.2f}, Max={np.max(data):.2f}, Mean={np.mean(data):.2f}")
    return data, spectra_to_plot, maps_to_plot

def _save_ground_truth_plot(spectra: list, maps: list, filename: str, energy_range: dict = None):
    """Saves a plot of the clean, ground-truth components."""
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
            # Plot spectrum
            ax_spec = axes[0, i]
            ax_spec.plot(x_axis, spectra[i], label=f"GT Comp {i+1}")
            ax_spec.set_title(spec_titles[i])
            ax_spec.set_xlabel(x_label)
            ax_spec.set_ylabel("Intensity (a.u.)")
            ax_spec.grid(True, alpha=0.3)
            
            # Plot map
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
    """
    Recursively traverses a dictionary or list, converting any sets to lists.
    This makes the object JSON serializable.
    """
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_sets_to_lists(element) for element in obj]
    return obj

def main():
    """
    Generates and saves the synthetic data and its corresponding metadata.
    """
    
    print("--- Generating Synthetic Hyperspectral Dataset (3-Component Gradient) ---")

    # --- THIS IS YOUR NEW CONTROL PANEL ---
    DATA_CONFIG = {
        "h": 100,
        "w": 100,
        "e": 256,
        "n_components": 3,
        "add_background_noise": False,
        "background_level": 0.1,
        "add_gaussian_noise": False,
        "gaussian_level": 0.05,
        "add_negative_noise": False,
        "negative_level": -0.5,
        "add_spikes": False,
        "n_spikes": 50,
        "spike_intensity": 1500.0
    }
    # ------------------------------------

    # 1. Create data and ground truth components
    data, gt_spectra, gt_maps = create_synthetic_data(DATA_CONFIG)
    
    # 2. Dynamically create the description for the metadata
    description_parts = [
        f"Synthetic 3-component data: Phase A (gradient), Phase B (gradient), and a distinct Interface."
    ]
    if DATA_CONFIG.get("add_spikes", False):
        description_parts.append("Contains high-intensity spikes.")
    
    system_info = {
        "experiment_type": "Spectroscopy",
        "experiment": {"technique": "Raman Map"},
        "sample": {"material": "Heterostructure"},
        "energy_range": {
            "start": 100,
            "end": 800,
            "units": "cm^-1",
        }
    }
    
    # 3. Define output filenames and directory
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    data_filename = os.path.join(output_dir, "synthetic_interface_data.npy")
    meta_filename = os.path.join(output_dir, "synthetic_interface_data.json")
    gt_plot_filename = os.path.join(output_dir, "synthetic_interface_ground_truth.png")
    
    # 4. Save the data as .npy
    try:
        np.save(data_filename, data)
        logger.info(f"Successfully saved synthetic data to: {data_filename}")
    except Exception as e:
        logger.error(f"Failed to save data file: {e}", exc_info=True)
        return

    # 5. Save the metadata as .json
    try:
        cleaned_system_info = convert_sets_to_lists(system_info)
        
        with open(meta_filename, 'w') as f:
            json.dump(cleaned_system_info, f, indent=4)
        logger.info(f"Successfully saved metadata to: {meta_filename}")
    except Exception as e:
        logger.error(f"Failed to save metadata file: {e}", exc_info=True)
        return
    
    # 6. Save the ground truth plot
    try:
        _save_ground_truth_plot(gt_spectra, gt_maps, gt_plot_filename, system_info.get("energy_range"))
    except Exception as e:
        logger.error(f"Failed to save ground truth plot: {e}", exc_info=True)
        
    print(f"\nSuccessfully created in '{output_dir}' directory:\n- {os.path.basename(data_filename)}\n- {os.path.basename(meta_filename)}\n- {os.path.basename(gt_plot_filename)}")    
    print("\nRun this script to generate the files. The .png file will show the 3 ground truth components.")

if __name__ == "__main__":
    # --- ALL DUPLICATE FUNCTIONS REMOVED ---
    # Now this just runs main()
    main()