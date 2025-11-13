import sys
import json
import numpy as np
import os

# Add the scilink path
sys.path.append("../")

# 1. Import your new data generator
import synthetic_data_gen as sdg

# 2. Import your Analysis Agent
from scilink.agents.exp_agents import HyperspectralAnalysisAgent

# --- SCRIPT START ---

print("--- Starting Pre-processing Agent Stress Test ---")



# 3. Get all predefined test cases
test_cases = sdg.get_test_case_configs()
print(f"Found {len(test_cases)} test cases: {list(test_cases.keys())}\n")

# 4. Loop through and run each test case
for case_name, case_config in test_cases.items():
    print(f"\n==================================================")
    print(f"🔬 RUNNING TEST CASE: {case_name}")
    print(f"==================================================")
    
    # 5. Define ONE output directory for *all* files for this case
    output_dir = f"test_run_output/{case_name}"
    
    # 6. Generate data, saving it directly into that directory
    file_paths = sdg.generate_dataset_and_save(
        data_config=case_config["data_config"],
        system_info=case_config["system_info"],
        base_filename=case_name,  # This will create 'case_name_data.npy'
        output_dir=output_dir   # <-- All files go here
    )

    data_path = file_paths["data_file"]
    system_info_path = file_paths["meta_file"]
    
    print(f"All files will be saved in: {output_dir}")
    print(f"Data: {data_path}")
    print(f"Metadata: {system_info_path}")

    # 7. Initialize a NEW agent, pointing to the *same* directory
    agent = HyperspectralAnalysisAgent(
        spectral_unmixing_settings = {'run_preprocessing': True},
        output_dir=output_dir  # <-- Agent results go here too
    )
    
    # 8. Run the agent
    print("Calling agent...")
    results = agent.analyze_hyperspectral_data(data_path, system_info_path)
    
    # 9. Print the final analysis
    print(f"\n--- 🤖 AGENT ANALYSIS FOR: {case_name} ---")
    print(results['detailed_analysis'])
    print(f"--------------------------------------\n")

print("✅ All test cases complete.")