import pandas as pd
names=['train','test']
for name in names:
    # Read the Parquet file.
    df = pd.read_parquet(f"data/MATH-TTT/{name}.parquet")
    # Take the first 32 rows.
    df_small = df.head(32)

    # Save as a new Parquet file (optional).
    df_small.to_parquet(f"data/MATH-TTT/{name}_debug.parquet")


    print(df_small.shape)
    print(df_small.head())
