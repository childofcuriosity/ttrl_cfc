import matplotlib
# Set Agg before importing pyplot for headless servers.
matplotlib.use('Agg')

import pandas as pd
import ast
import os
import glob
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
# Add the server's verl checkout to the import path.
from verl.utils.reward_score.ttrl_math import extract_answer, grade


class MathEquivalenceUF:
    """Union-find implementation matching the original code."""
    def __init__(self, fast_mode=False): # Callers explicitly use False.
        self.parent = {}
        self.fast_mode = fast_mode

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            return x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        if x is None or y is None:
            return False
        if self._are_equivalent(x, y):
            rx, ry = self.find(x), self.find(y)
            if rx != ry:
                self.parent[ry] = rx
            return True
        return False

    def _are_equivalent(self, a, b):
        try:
            # fast_mode is passed as False by the caller.
            return grade(a, b, fast=self.fast_mode) and grade(b, a, fast=self.fast_mode)
        except Exception:
            return False

def calculate_pseudo_for_subset(extracted_answers, gt, n):
    """
    Match the original _covalidate voting logic:
    1. Take the first n samples.
    2. Build equivalence classes.
    3. Select the majority vote after excluding empty strings.
    4. grade(representative, gt, fast=False)
    """
    subset = extracted_answers[:n]
    if not subset:
        return False

    # 1. Reconstruct equivalence classes with fast_mode=False.
    uf = MathEquivalenceUF(fast_mode=False)

    for idx_a in range(len(subset)):
        a = subset[idx_a]
        # Get the current representatives.
        represents = [x for x, p in uf.parent.items() if x == p]
        matched = False
        for rep in represents:
            if uf.union(a, rep):
                matched = True
                break
        if not matched and a not in uf.parent:
            uf.parent[a] = a

    # 2. Reconstruct vote counts.
    vote_counter = Counter()
    for ans in subset:
        root = uf.find(ans)
        vote_counter[root] += 1

    # 3. Prefer nonempty representatives, matching the original selection.
    non_empty_votes = [(ans, cnt) for ans, cnt in vote_counter.most_common() if ans.strip() != ""]

    if len(non_empty_votes) > 0:
        representative, vote_count = non_empty_votes[0]
    else:
        # Fall back when every answer is empty.
        if not vote_counter: return False
        representative, vote_count = vote_counter.most_common(1)[0]

    # 4. Grade the answer with fast=False.
    return grade(representative, gt, fast=False)
def analyze_3d_performance(expname):
    # Match input files.
    pattern = os.path.join(expname, "covalidate_preload_t=*.csv")
    files = glob.glob(pattern)
    if not files:
        print(f"Error: No files found in {expname}")
        return

    n_votes_list = [16, 32, 48, 64]
    plot_data = []

    for file_path in files:
        # Extract the temperature from the filename.
        match = re.search(r"t=(\d+\.?\d*)", os.path.basename(file_path))
        if not match: continue
        temp = float(match.group(1))

        print(f"Processing Temperature t={temp} ...")
        df = pd.read_csv(file_path)

        # Parse serialized lists into Python lists.
        df['votes_extract'] = df['votes_extract'].apply(ast.literal_eval)

        for n in n_votes_list:
            correct_count = 0
            for idx, row in df.iterrows():
                if calculate_pseudo_for_subset(row['votes_extract'], row['ground_truth'], n):
                    correct_count += 1

            acc = (correct_count / len(df)) * 100
            plot_data.append({'temp': temp, 'n_votes': n, 'acc': acc})
            print(f"  N={n} | Accuracy = {acc:.2f}%")

    # Plot results.
    df_plot = pd.DataFrame(plot_data).sort_values(['temp', 'n_votes'])
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    temps = sorted(df_plot['temp'].unique())
    votes = n_votes_list
    _x, _y = np.meshgrid(np.arange(len(temps)), np.arange(len(votes)))
    x, y = _x.ravel(), _y.ravel()

    z = np.zeros_like(x)
    dz = []
    for i in range(len(x)):
        t = temps[x[i]]
        v = votes[y[i]]
        val = df_plot[(df_plot['temp'] == t) & (df_plot['n_votes'] == v)]['acc'].values[0]
        dz.append(val)

    dx = dy = 0.4
    colors = plt.cm.plasma(np.array(dz) / 100.0)
    ax.bar3d(x, y, z, dx, dy, dz, color=colors, alpha=0.8)

    ax.set_xticks(np.arange(len(temps)) + dx/2)
    ax.set_xticklabels(temps)
    ax.set_yticks(np.arange(len(votes)) + dy/2)
    ax.set_yticklabels(votes)

    ax.set_xlabel('Temperature (t)')
    ax.set_ylabel('Number of Votes (N)')
    ax.set_zlabel('Accuracy (%)')
    ax.set_zlim(0, 100)
    ax.set_title(f'Strict 3D Accuracy Analysis: {expname}')

    # Save the figure.
    output_img = os.path.join(expname, "3d_vote_analysis_server.png")
    plt.savefig(output_img, dpi=150)
    print(f"\n[DONE] Plot saved to: {output_img}")

if __name__ == "__main__":
    try:
        with open("expname.txt", "r", encoding="utf-8") as f:
            expname = f.readline().strip()
    except:
        expname = "."
    analyze_3d_performance(expname)
