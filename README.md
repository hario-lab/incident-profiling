# Incident Profiling for Ransomware Actor Attribution

## Methodology

*Incident Profiling* is an analytical framework originally proposed by Daiji HARIO, Ph.D. (2026) for ransomware actor attribution.

It treats each TTP as a binary outcome of tactical decision-making — adopted (1) or not adopted (0) — and measures similarity between incidents using Manhattan distance, reflecting the semantic distinction between "not adopted" and "not recorded." The resulting distance matrix is visualized through non-metric MDS to construct a *tactical space* in which ransomware actor groups form identifiable clusters and new incidents can be positioned for early-stage attribution.

If you use or build upon this framework, please cite the original paper (see [Citation](#citation)).

---

## Overview

This repository provides the Python implementation accompanying the paper.  
The code constructs a **tactical space** from binary TTP (Tactics, Techniques, and Procedures) data using **Manhattan distance** and **non-metric Multidimensional Scaling (MDS)**, enabling ransomware actor attribution based solely on publicly available information.

Key features:
- Binary TTP matrix construction from public incident reports
- Manhattan (Hamming) distance calculation — treating TTP non-adoption as a deliberate tactical choice
- Non-metric MDS visualization of tactical similarity structure
- Placement of new (unknown) incidents into the existing tactical space

---

## Repository Structure

```
/
├── README.md
├── LICENSE
├── incident_profiling.py       # Main analysis script (Appendix 2 of the paper)
└── sample/
    └── ttp_matrix_sample.csv   # Sample input data (dummy incidents)
```

---

## Requirements

Python 3.8 or later. Install dependencies with:

```bash
pip install pandas numpy scikit-learn matplotlib
```

---

## Input Format

Prepare a CSV file (`ttp_matrix.csv`) with the following structure:

| incident_id | group   | RDP | SMB | WMI | LSASS | Kerberoast | AVstop | LogDel | Rclone | StealBit | Tor | ESXi | Backup | RustGo | VPN |
|-------------|---------|-----|-----|-----|-------|------------|--------|--------|--------|----------|-----|------|--------|--------|-----|
| RSa001      | LockBit | 1   | 1   | 0   | 1     | 0          | 1      | 1      | 0      | 1        | 1   | 1    | 1      | 1      | 1   |

- Each row = one incident
- `incident_id`: unique identifier
- `group`: ransomware group label
- Remaining columns: binary TTP indicators (1 = confirmed, 0 = not adopted)

A sample file is provided in `sample/ttp_matrix_sample.csv`.

---

## Usage

```bash
python incident_profiling.py
```

By default, the script reads `ttp_matrix.csv` in the current directory.  
Edit the `DATA_FILE` variable at the top of the script to specify a different path.

### Output

| File | Description |
|------|-------------|
| `tactical_space.png` | 2-D MDS scatter plot of all incidents |
| `distance_matrix.csv` | Pairwise Manhattan distance matrix |

---

## Distance Metric Note

This implementation uses **Manhattan distance** as the default, consistent with the paper's theoretical framework: a TTP value of `0` is interpreted as **deliberate non-adoption**, not missing data.

To use **Jaccard distance** instead (appropriate when `0` represents unobserved/unreported behavior), change line in the script:

```python
# Manhattan (default — symmetric, treats 0 as "not adopted")
D = pairwise_distances(X, metric="manhattan")

# Jaccard (alternative — asymmetric, treats 0 as missing)
D = pairwise_distances(X, metric="jaccard")
```

See Sections 2.3 and 3.4 of the paper for the theoretical rationale.

---

## Citation

**Code repository:** https://github.com/hario-lab/incident-profiling  
**Code DOI:** https://doi.org/10.5281/zenodo.19478411

---

## License

MIT License. See [LICENSE](LICENSE) for details.
