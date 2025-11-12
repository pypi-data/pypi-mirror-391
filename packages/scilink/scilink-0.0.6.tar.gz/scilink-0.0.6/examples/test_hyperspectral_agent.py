import sys
sys.path.append("../")

from scilink.agents.exp_agents import HyperspectralAnalysisAgent


data_path="data/eels_plasmon2.npy"
system_info="data/eels_plasmon2.json"

agent = HyperspectralAnalysisAgent(run_preprocessing=True)
results = agent.analyze_hyperspectral_data(data_path, system_info)
print(results['detailed_analysis'])