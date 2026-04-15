from simulation.simulator import data
import pandas as pd

# Create the DataFrame
df = pd.DataFrame(data)

# Save it to your computer with a specific name
df.to_excel("stock_simulation_results.xlsx", index=False)

print("File saved successfully!")
