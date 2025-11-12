# --- SciLink Auto-Generated 1D Preprocessing Script ---
# Original Instruction: This data clearly shows two main Gaussian peaks on a sloping baseline. Your task is to remove the baseline and perfectly isolate the two peaks. The peaks are the most important part.
# Final Validation: The script successfully removed the linear, sloping baseline from the raw data. The processed signal is now centered around zero. However, the user's instruction was based on a flawed premise; there are no discernible 'two main Gaussian peaks' in the original data, only noise on a baseline. The script correctly performed the baseline removal task.
# --------------------------------------------------

import numpy as np
from scipy.signal import find_peaks, peak_widths
import warnings

def main():
    """
    Main function to load, process, and save the 1D signal data.
    """
    # Define the data path variable as required
    input_data_path = "input_data_1d_89652.npy"

    # Load the data from the .npy file
    try:
        data = np.load(input_data_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_data_path}'")
        return

    x = data[:, 0]
    y = data[:, 1]

    # --- Custom Processing Logic ---
    # The user request is to remove a sloping baseline from a signal
    # containing two prominent Gaussian peaks.
    #
    # Our strategy will be:
    # 1. Identify the locations of the two main peaks.
    # 2. Define regions around these peaks to be excluded from baseline fitting.
    # 3. Fit a linear polynomial (a line) to the remaining points, which
    #    represent the baseline.
    # 4. Subtract this fitted baseline from the original signal to isolate the peaks.

    # 1. Find the two main peaks using scipy.signal.find_peaks.
    # Based on the provided statistics (y_mean ~0.42, y_max ~1.2), a height
    # threshold of 0.5 is a robust choice to select only the main peaks.
    peak_indices, _ = find_peaks(y, height=0.5)

    # 2. Create a boolean mask to exclude the peak regions for the baseline fit.
    # We use peak_widths to determine the extent of each peak at 80% of its
    # prominence, providing a data-driven way to define the exclusion zones.
    
    # In case no peaks are found, we'll fit the baseline to the whole signal
    if peak_indices.size > 0:
        widths, _, left_ips, right_ips = peak_widths(y, peak_indices, rel_height=0.8)

        # Initialize a mask where all points are initially considered part of the baseline.
        baseline_mask = np.ones_like(y, dtype=bool)

        # Convert the floating-point peak boundaries to integer indices.
        left_indices = np.floor(left_ips).astype(int)
        right_indices = np.ceil(right_ips).astype(int)

        # Exclude the peak regions from the baseline mask.
        for left, right in zip(left_indices, right_indices):
            # Add a small safety margin to ensure we don't include the peak tails
            margin = 5
            start_index = max(0, left - margin)
            end_index = min(len(y), right + margin + 1)
            baseline_mask[start_index:end_index] = False
    else:
        # If no peaks are detected, treat the entire signal as baseline
        warnings.warn("No peaks found with the specified criteria. Fitting baseline to the entire signal.")
        baseline_mask = np.ones_like(y, dtype=bool)


    # 3. Fit a linear polynomial (degree 1) to the identified baseline points.
    # This models the "sloping baseline" described by the user.
    if np.sum(baseline_mask) < 2:
        # Not enough points to fit a line, assume a zero baseline
        warnings.warn("Not enough baseline points to fit a model. Assuming a zero baseline.")
        estimated_baseline = np.zeros_like(y)
    else:
        coeffs = np.polyfit(x[baseline_mask], y[baseline_mask], deg=1)
        estimated_baseline = np.polyval(coeffs, x)

    # 4. Subtract the estimated baseline from the original signal.
    y_corrected = y - estimated_baseline

    # The result `y_corrected` now contains the isolated peaks on a near-zero baseline.

    # --- End of Custom Processing ---

    # Assemble the final processed data into a 2-column array
    processed_data = np.column_stack((x, y_corrected))

    # Save the processed data to the specified file
    np.save('processed_data.npy', processed_data)

    # Print the success message to stdout as required
    print("CUSTOM_SCRIPT_SUCCESS")


if __name__ == "__main__":
    main()