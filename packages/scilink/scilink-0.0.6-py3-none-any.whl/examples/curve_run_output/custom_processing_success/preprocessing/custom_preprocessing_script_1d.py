# --- SciLink Auto-Generated 1D Preprocessing Script ---
# Original Instruction: This data has a strong sloping baseline that is hiding the peaks. Please use a robust method like Asymmetric Least Squares (ALS) or a polynomial fit from scipy or sklearn to remove this baseline.
# Final Validation: The script successfully removed the strong, sloping baseline as requested. The two primary peaks are now clearly visible and centered around a y-value of zero, and their shapes appear well-preserved without significant distortion.
# --------------------------------------------------

import numpy as np
import warnings

def main():
    """
    Main function to perform baseline correction on 1D signal data.
    """
    # Define the input data path as required
    input_data_path = "input_data_1d_89652.npy"

    # Load the 2-column (X, Y) data
    data = np.load(input_data_path)
    x = data[:, 0]
    y = data[:, 1]

    # --- Custom Processing: Baseline Removal ---
    # The user's request is to remove a "strong sloping baseline" to reveal peaks.
    # A polynomial fit is a robust and effective method for this type of baseline.
    # We will fit a low-order polynomial to the data, which will represent the
    # overall trend (the baseline), and then subtract it.

    # A polynomial degree of 5 is chosen as a good trade-off. It's flexible
    # enough to capture a non-linear sloping baseline but not so high that it
    # starts fitting the actual peaks.
    poly_degree = 5

    # FIX: The attribute `np.RankWarning` has been removed in modern versions of NumPy.
    # The warning suppression code block caused an AttributeError.
    # The most direct fix is to remove the attempt to suppress this specific,
    # non-existent warning. The polyfit function will still work correctly.
    
    # Fit polynomial to the data
    coeffs = np.polyfit(x, y, poly_degree)

    # Evaluate the polynomial at the x-coordinates to get the baseline
    baseline = np.polyval(coeffs, x)

    # Subtract the baseline from the original y-data to get the corrected signal
    y_corrected = y - baseline

    # Assemble the final processed data into a 2-column array
    processed_data = np.column_stack((x, y_corrected))

    # Save the processed data to the specified file
    np.save('processed_data.npy', processed_data)

    # Print the success message to stdout
    print("CUSTOM_SCRIPT_SUCCESS")


if __name__ == "__main__":
    main()