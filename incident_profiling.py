"""
Incident Profiling via Non-Metric MDS
================================================

This script reproduces the tactical space construction described in the paper:
"Ransomware Attribution through Incident Profiling: A TTP-Based Approach
for CSIRT Decision Support"

It reads a binary TTP matrix from a CSV file, computes Manhattan distances,
applies non-metric MDS, and outputs a 2-D scatter plot.

Input CSV format (example):
    incident_id, group, RDP, SMB, WMI, LSASS, ...
    RSa001, LockBit, 1, 1, 0, 1, ...
    RSa002, LockBit, 1, 0, 1, 1, ...
    ...

Requirements:
    pip install pandas numpy scikit-learn matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.manifold import MDS
from sklearn.metrics import pairwise_distances

# -----------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------
DATA_FILE  = "ttp_matrix.csv"   # Path to your CSV file
ID_COL     = "incident_id"      # Column name for incident IDs
GROUP_COL  = "group"            # Column name for group labels

# -----------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------
df     = pd.read_csv(DATA_FILE)
ids    = df[ID_COL].tolist()
groups = df[GROUP_COL].tolist()

# Binary TTP matrix (rows = incidents, columns = TTP variables)
X = df.drop(columns=[ID_COL, GROUP_COL]).values.astype(int)
print(f"Loaded {X.shape[0]} incidents x {X.shape[1]} TTP variables")

# -----------------------------------------------------------------------
# Compute Manhattan (Hamming) distance matrix
#
# Manhattan distance is used because TTP values represent deliberate
# tactical choices ("adopted / not adopted"), not observed / missing data.
# See Sections 2.3 and 3.4 of the paper.
#
# To use Jaccard distance instead (appropriate when 0s represent missing
# observations rather than deliberate non-adoption), change the metric:
#   metric="jaccard"
# -----------------------------------------------------------------------
D = pairwise_distances(X, metric="manhattan")
print(f"Distance matrix shape: {D.shape}")
print(f"Distance range: {D.min():.2f} - {D.max():.2f}")

# -----------------------------------------------------------------------
# Apply non-metric MDS
#
# Non-metric MDS preserves the rank order of distances, which is
# appropriate for binary data where absolute distance values are less
# meaningful than their ordinal relationships (see Section 3.5).
#
# Parameters:
#   n_components : dimensionality of the output space (2 for visualization)
#   n_init       : number of random initializations (increase for stability)
#   max_iter     : maximum iterations per initialization
#   random_state : fix for reproducibility
# -----------------------------------------------------------------------
mds = MDS(
    n_components=2,
    metric=False,               # False = non-metric MDS
    dissimilarity="precomputed",
    n_init=10,
    max_iter=300,
    random_state=42,
)

coords  = mds.fit_transform(D)
stress  = mds.stress_

# Kruskal normalized Stress-1
stress1 = np.sqrt(stress / np.sum(D ** 2))
print(f"Stress (raw):        {stress:.4f}")
print(f"Stress-1 (Kruskal):  {stress1:.4f}")
print("Kruskal fit criteria: <0.025 Excellent, <0.05 Good, <0.10 Fair, <0.20 Poor")

# -----------------------------------------------------------------------
# Plot tactical space
# -----------------------------------------------------------------------
unique_groups = sorted(set(groups))
colors        = cm.tab10(np.linspace(0, 1, len(unique_groups)))
color_map     = {g: c for g, c in zip(unique_groups, colors)}

fig, ax = plt.subplots(figsize=(10, 7))

for g in unique_groups:
    idx = [i for i, grp in enumerate(groups) if grp == g]
    ax.scatter(
        coords[idx, 0], coords[idx, 1],
        color=color_map[g], label=g, s=60, zorder=3
    )

# Annotate each point with its incident ID
for i, label in enumerate(ids):
    ax.annotate(
        label, (coords[i, 0], coords[i, 1]),
        fontsize=7, ha="left", va="bottom",
        xytext=(3, 3), textcoords="offset points"
    )

ax.axhline(0, color="lightgray", linewidth=0.5, zorder=0)
ax.axvline(0, color="lightgray", linewidth=0.5, zorder=0)
ax.set_xlabel("Dimension 1")
ax.set_ylabel("Dimension 2")
ax.set_title(
    f"Tactical Space — Non-Metric MDS  (Stress-1 = {stress1:.3f})",
    fontsize=12
)
ax.legend(title="Group", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("tactical_space.png", dpi=150, bbox_inches="tight")
plt.show()
print("Plot saved to tactical_space.png")

# -----------------------------------------------------------------------
# Export distance matrix (optional)
# -----------------------------------------------------------------------
dist_df = pd.DataFrame(D, index=ids, columns=ids)
dist_df.to_csv("distance_matrix.csv")
print("Distance matrix saved to distance_matrix.csv")
