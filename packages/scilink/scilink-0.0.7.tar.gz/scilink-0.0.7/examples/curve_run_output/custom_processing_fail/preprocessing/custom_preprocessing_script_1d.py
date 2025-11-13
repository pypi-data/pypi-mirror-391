# --- SciLink Auto-Generated 1D Preprocessing Script ---
# Original Instruction: This data clearly shows two main Gaussian peaks on a sloping baseline. Your task is to remove the baseline and perfectly isolate the two peaks. The peaks are the most important part.
# Final Validation: The script successfully removed the sloping baseline trend. However, the user's assertion that the raw data contains 'two main Gaussian peaks' is incorrect. The signal appears to be random noise superimposed on a linear baseline. After removing the baseline, the result is simply centered random noise, which fails to isolate the non-existent peaks.
# --------------------------------------------------

import numpy as np
import warnings

def main():
    """
    Loads a 2-column signal, identifies and removes a sloping linear baseline,
    isolates the positive peaks, and saves the processed data.
    """
    # Define the input data path as required
    input_data_path = "input_data_1d_61694.npy"

    # Load the data from the .npy file
    data = np.load(input_data_path)
    x = data[:, 0]
    y = data[:, 1]

    # --- Custom Processing: Iterative Baseline Correction ---
    # The user described a "sloping baseline" with two peaks on top. A robust
    # method to remove such a baseline is an iterative polynomial fit.
    # This algorithm repeatedly fits a polynomial to the data, but in each
    # subsequent iteration, it gives less weight to the points identified as
    # peaks (points above the fitted line), causing the fit to converge on
    # the true baseline underneath the peaks.

    # A simple and effective implementation is to replace peak values with the
    # current baseline estimate for the next iteration's fit.
    
    # We will use a degree 1 polynomial (a straight line) for the "sloping baseline".
    poly_degree = 1
    
    # Number of iterations for the baseline to converge
    num_iterations = 10
    
    # Use a copy of the y-data for the iterative process
    y_for_fit = np.copy(y)

    # To handle potential RankWarning if the data for fitting becomes ill-conditioned
    with warnings.catch_warnings():
        # In modern versions of NumPy, RankWarning was moved to the exceptions submodule.
        # The original `np.RankWarning` caused an AttributeError.
        warnings.simplefilter('ignore', np.exceptions.RankWarning)
        
        # Loop to iteratively refine the baseline
        for _ in range(num_iterations):
            # Fit a polynomial to the current version of the data
            coeffs = np.polyfit(x, y_for_fit, poly_degree)
            
            # Evaluate the polynomial to get the current baseline estimate
            baseline_estimate = np.polyval(coeffs, x)
            
            # For the next iteration, update y_for_fit: where the original signal (y)
            # is above the baseline, replace it with the baseline value.
            # This effectively "chops off" the peaks.
            y_for_fit = np.minimum(y, baseline_estimate)

    # After the iterations, the final `baseline_estimate` is our model of the baseline
    final_baseline = baseline_estimate
    
    # Remove the baseline from the original signal
    y_corrected = y - final_baseline
    
    # To "perfectly isolate the two peaks", we set the new baseline to zero.
    # Any negative values resulting from noise are clipped to zero.
    y_processed = np.maximum(0, y_corrected)

    # --- Save the Processed Data ---
    # Combine the original x-values with the processed y-values
    processed_data = np.column_stack((x, y_processed))
    
    # Save the result to the specified output file
    np.save('processed_data.npy', processed_data)
    
    # Print the success message to stdout
    print("CUSTOM_SCRIPT_SUCCESS")


if __name__ == "__main__":
    main()