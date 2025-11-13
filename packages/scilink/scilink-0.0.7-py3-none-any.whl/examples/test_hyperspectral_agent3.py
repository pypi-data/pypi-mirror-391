import sys
sys.path.append("../")

import synthetic_data_gen as sdg
from scilink.agents.exp_agents import HyperspectralAnalysisAgent

print("=" * 60)
print("HYPERSPECTRAL ANALYSIS AGENT TEST")
print("=" * 60)

# Get all available test cases
test_cases = sdg.get_test_case_configs()

# ============================================================================
# TEST 1: Clean Data (Baseline - Should work perfectly)
# ============================================================================
print("\n" + "=" * 60)
print("TEST 1: Clean Data (No Corruption)")
print("=" * 60)

# Generate clean synthetic data
clean_files = sdg.generate_dataset_and_save(
    data_config=test_cases["clean_substrate"]["data_config"],
    system_info=test_cases["clean_substrate"]["system_info"],
    base_filename="clean_test",
    output_dir="test_results/clean"
)

# Run analysis (preprocessing enabled by default)
agent_clean = HyperspectralAnalysisAgent(
    output_dir="test_results/clean"
)

results_clean = agent_clean.analyze_hyperspectral_data(
    data_path=clean_files["data_file"],
    metadata_path=clean_files["meta_file"]
)

print(results_clean['detailed_analysis'])

# ============================================================================
# TEST 2: Spike Nightmare WITHOUT Preprocessing (Should Fail)
# ============================================================================
print("\n\n" + "=" * 60)
print("TEST 2: Spike Nightmare WITHOUT Preprocessing")
print("=" * 60)

# Generate spike nightmare data
spike_files = sdg.generate_dataset_and_save(
    data_config=test_cases["spike_nightmare"]["data_config"],
    system_info=test_cases["spike_nightmare"]["system_info"],
    base_filename="spike_no_preproc",
    output_dir="test_results/spike_no_preproc"
)

# Run analysis with preprocessing DISABLED
agent_no_preproc = HyperspectralAnalysisAgent(
    run_preprocessing=False,  # ← Turn OFF preprocessing
    output_dir="test_results/spike_no_preproc"
)

results_no_preproc = agent_no_preproc.analyze_hyperspectral_data(
    data_path=spike_files["data_file"],
    metadata_path=spike_files["meta_file"]
)

print(results_no_preproc['detailed_analysis'])

# ============================================================================
# TEST 3: Spike Nightmare WITH Preprocessing (Should Succeed)
# ============================================================================
print("\n\n" + "=" * 60)
print("TEST 3: Spike Nightmare WITH Preprocessing")
print("=" * 60)

# Generate spike nightmare data again (same config)
spike_files_preproc = sdg.generate_dataset_and_save(
    data_config=test_cases["spike_nightmare"]["data_config"],
    system_info=test_cases["spike_nightmare"]["system_info"],
    base_filename="spike_with_preproc",
    output_dir="test_results/spike_with_preproc"
)

# Run analysis with preprocessing ENABLED
agent_with_preproc = HyperspectralAnalysisAgent(
    run_preprocessing=True,  # ← Turn ON preprocessing
    output_dir="test_results/spike_with_preproc"
)

results_with_preproc = agent_with_preproc.analyze_hyperspectral_data(
    data_path=spike_files_preproc["data_file"],
    metadata_path=spike_files_preproc["meta_file"]
)

print(results_with_preproc['detailed_analysis'])

# ============================================================================
# SUMMARY
# ============================================================================
print("\n\n" + "=" * 60)
print("TEST SUMMARY")
print("\nCheck the folders:")
print("  - test_results/clean/")
print("  - test_results/spike_no_preproc/")
print("  - test_results/spike_with_preproc/")
print("\n✅ All tests complete!")
