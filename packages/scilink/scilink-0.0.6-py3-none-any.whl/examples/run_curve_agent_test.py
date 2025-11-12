import sys
import json
import numpy as np
import os

# Add the scilink path
sys.path.append("../")

# 1. Import your new curve data generator
import generate_curve_test_cases as cdg  # <-- CHANGED

# 2. Import your Curve Fitting Agent
from scilink.agents.exp_agents import CurveFittingAgent  # <-- CHANGED

# --- SCRIPT START ---

print("--- Starting Curve Pre-processing Agent Test ---")

# 3. Get all predefined test cases
test_cases = cdg.get_test_case_configs()  # <-- CHANGED
print(f"Found {len(test_cases)} test cases: {list(test_cases.keys())}\n")

# 4. Loop through and run each test case
for case_name, case_config in test_cases.items():
    print(f"\n==================================================")
    print(f"🔬 RUNNING TEST CASE: {case_name}")
    print(f"==================================================")
    
    # 5. Define ONE output directory for *all* files for this case
    #    (Using a different root folder for clarity)
    output_dir = f"curve_run_output/{case_name}"  # <-- CHANGED
    
    # 6. Generate data, saving it directly into that directory
    file_paths = cdg.generate_dataset_and_save(  # <-- CHANGED
        data_config=case_config["data_config"],
        system_info=case_config["system_info"],
        base_filename=case_name,
        output_dir=output_dir   # <-- All files go here
    )

    data_path = file_paths["data_file"]
    system_info_path = file_paths["meta_file"]
    
    print(f"All files will be saved in: {output_dir}")
    print(f"Data: {data_path}")
    print(f"Metadata: {system_info_path}")

    # 7. Initialize a NEW agent, pointing to the *same* directory
    #    The CurveFittingAgent will automatically use its CurvePreprocessingAgent
    agent = CurveFittingAgent(  # <-- CHANGED
        run_preprocessing=True,
        output_dir=output_dir,  # <-- Agent results go here too
    )
    
    # 8. Run the agent
    print("Calling agent...")
    # --- CHANGED: Call analyze_for_claims ---
    # We pass the system_info_path directly. The BaseAnalysisAgent handles loading it.
    results = agent.analyze_for_claims(data_path, system_info=system_info_path)
    
    # 9. Print the final analysis
    print(f"\n--- 🤖 AGENT ANALYSIS FOR: {case_name} ---")
    if results.get("status") == "success":
        print(results.get('detailed_analysis', 'No detailed analysis found.'))
        claims = results.get('scientific_claims', [])
        if claims:
            print("\n**Scientific Claims:**")
            for i, claim in enumerate(claims):
                print(f"  {i+1}. {claim['claim']}")
    else:
        print(f"🔥 Agent analysis FAILED:")
        print(results.get("message", "Unknown error"))
    print(f"--------------------------------------\n")

print("✅ All test cases complete.")