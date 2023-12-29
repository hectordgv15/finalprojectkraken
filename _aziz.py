import pandas as pd
import numpy as np

# Creating a sample DataFrame
np.random.seed(42)  # Setting seed for reproducibility

data = pd.DataFrame({"pctK": np.random.randint(0, 100, 2000), "pctD": np.random.randint(0, 100, 2000)})

data["Buy_Signal"] = np.where(
    (data["pctK"] > data["pctD"]) & (data["pctK"].shift(1) < data["pctD"].shift(1)) & (data["pctK"] < 20),
    1,
    0,
)

data["Buy_Signal_2"] = (
    (data["pctK"] > data["pctD"]) & (data["pctK"].shift(1) < data["pctD"].shift(1)) & (data["pctK"] < 20)
).astype(int)


data["Sell_Signal"] = np.where(
    (data["pctK"] < data["pctD"]) & (data["pctK"].shift(1) > data["pctD"].shift(1)) & (data["pctK"] > 80),
    1,
    0,
)


data["Sell_Signal_2"] = (
    (data["pctK"] < data["pctD"]) & (data["pctK"].shift(1) > data["pctD"].shift(1)) & (data["pctK"] > 80)
).astype(int)


print("Sample")
