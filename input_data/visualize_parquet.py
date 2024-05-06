import pandas as pd
result = pd.read_parquet('data/part.0.parquet', engine='pyarrow')
print(result)