import pandas as pd

def write_csv(results, path="outputs/analysis.csv"):
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)
