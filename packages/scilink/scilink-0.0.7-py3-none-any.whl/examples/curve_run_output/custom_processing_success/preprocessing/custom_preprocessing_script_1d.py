# --- SciLink Auto-Generated 1D Preprocessing Script ---
# Original Instruction: This data has a strong sloping baseline that is hiding the peaks. Please use a robust method like Asymmetric Least Squares (ALS) or a polynomial fit from scipy or sklearn to remove this baseline.
# Final Validation: The script successfully removed the strong, sloping baseline from the raw data. The two underlying peaks are now clearly visible against a flat baseline centered near zero, and their shapes and relative heights appear to be perfectly preserved.
# --------------------------------------------------

import numpy as np
from scipy.sparse import csc_matrix, diags
from scipy.sparse.linalg import spsolve
import warnings

def main():
    """
    Main function to load, process, and save the 1D curve data.
    """
    # Define the path to the input data file as required.
    input_data_path = "input_data_1d_61694.npy"

    # Load the data from the .npy file.
    # The data is expected to be a 2-column array (X, Y).
    data = np.load(input_data_path)
    x = data[:, 0]
    y = data[:, 1]

    # --- Custom Processing: Asymmetric Least Squares (ALS) Baseline Correction ---
    # The user requested a robust method like ALS or a polynomial fit to remove
    # a strong sloping baseline. ALS is generally superior for this task as it
    # can fit a flexible baseline to the signal's minima without being
    # distorted by the presence of peaks. A standard polynomial fit often gets
    # pulled upwards by peaks, leading to over-correction.
    #
    # We will implement the ALS algorithm using scipy's sparse matrix tools.
    #
    # Parameters:
    # - lam (lambda): Smoothness parameter. A larger value results in a smoother baseline.
    # - p: Asymmetry parameter. Should be between 0 and 1. A value closer to 0
    #   gives more weight to points below the baseline, effectively ignoring peaks.
    # - n_iter: Number of iterations to converge on the baseline.

    def asymmetric_least_squares(y, lam=1e7, p=0.01, n_iter=10):
        """
        Implementation of the Asymmetric Least Squares (ALS) baseline correction algorithm.
        Based on the paper by P. Eilers and H. Boelens (2005).
        """
        L = len(y)
        # Create the second-order difference matrix operator
        D_op = diags([1, -2, 1], [0, 1, 2], shape=(L-2, L), format='csc')
        
        # The penalty matrix is formed by D.T @ D
        D = D_op.T @ D_op
        
        w = np.ones(L)
        
        with warnings.catch_warnings():
            # The spsolve function may raise warnings which are not critical for this
            # application and can be safely ignored.
            # FIX: Replaced 'VisibleDeprecationWarning' with the standard built-in
            # 'DeprecationWarning' to resolve the NameError from the original script.
            warnings.simplefilter("ignore", category=DeprecationWarning)
            warnings.simplefilter("ignore", category=FutureWarning)
            
            z = np.zeros_like(y)
            for i in range(n_iter):
                W = diags(w, 0, shape=(L, L), format='csc')
                # Solve the weighted least squares problem
                Z = W + lam * D
                z = spsolve(Z, w * y)
                # Update weights asymmetrically
                w = p * (y > z) + (1 - p) * (y <= z)

        return z

    # Apply the ALS algorithm to calculate the baseline
    # A high lambda is chosen for a very smooth baseline, fitting the "strong sloping" description.
    # A low p is chosen to aggressively ignore the positive peaks.
    baseline = asymmetric_least_squares(y, lam=1e7, p=0.001, n_iter=15)

    # Subtract the calculated baseline from the original y-data
    y_corrected = y - baseline

    # --- End of Custom Processing ---

    # Prepare the final processed data by combining the original x-column
    # with the newly calculated, baseline-corrected y-column.
    processed_data = np.column_stack((x, y_corrected))

    # Save the processed data to the specified output file.
    np.save('processed_data.npy', processed_data)

    # Print the success message to stdout as required.
    print("CUSTOM_SCRIPT_SUCCESS")


if __name__ == "__main__":
    main()