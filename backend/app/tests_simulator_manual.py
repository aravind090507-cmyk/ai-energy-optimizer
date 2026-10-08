import sys
import os

# Adjust path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.dataset_generator import load_real_dataset
from app.data_pipeline import clean_data
from app.simulator import simulate_scenario

def main():
    print("Loading dataset manually...")
    raw_df = load_real_dataset()
    
    print("Cleaning dataset...")
    df = clean_data(raw_df)
    
    print("\n--- Running Shift HVAC/AC by -2 Hours ---")
    res_shift = simulate_scenario(df, "HVAC/AC", "shift_hours", -2)
    print("Result shift:", res_shift)
    
    print("\n--- Running Reduce Kitchen by 30% ---")
    res_reduce = simulate_scenario(df, "Kitchen", "reduce_pct", 30)
    print("Result reduce:", res_reduce)

if __name__ == "__main__":
    main()
