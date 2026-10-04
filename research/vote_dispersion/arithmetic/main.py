import pandas as pd

def generate_arithmetic_dataset():
    samples = []
    ops = ['+', '-', '*', '/']
    for a in range(0, 10000):
        for b in range(0, 10000):
            for op in ops:
                if op == '+':
                    ans = a + b
                elif op == '-':
                    ans = a - b
                elif op == '*':
                    ans = a * b
                else:  # Division
                    if b == 0 or a % b != 0:
                        continue
                    ans = a // b
                if 0 <= ans <= 9:
                    samples.append({
                        "prompt": f"{a} {op} {b} = ",
                        "ground_truth": str(ans)
                    })
    return samples

# Generate the dataset.
data = generate_arithmetic_dataset()

# Convert to a DataFrame and save.
df = pd.DataFrame(data, columns=["prompt", "ground_truth"])
csv_path = "arithmetic_dataset.csv"
df.to_csv(csv_path, index=False, encoding="utf-8")

