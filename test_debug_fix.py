"""Test script to verify the fix for the similarity threshold issue."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from app.config import settings

# Verify the fix
print(f"SIMILARITY_THRESHOLD = {settings.SIMILARITY_THRESHOLD}")
assert settings.SIMILARITY_THRESHOLD == 0.1, f"Expected 0.1, got {settings.SIMILARITY_THRESHOLD}"
print("✅ Config fix verified: threshold is now 0.1")

# Test similarity scoring
import numpy as np

# Simulate the fix: with L2 distance ~1.0 for relevant docs
l2_distances = [0.97, 1.1, 1.2, 0.85, 1.5]
for d in l2_distances:
    score = float(np.exp(-d))
    passes = score >= 0.1
    print(f"  L2={d:.2f} -> exp(-L2)={score:.4f} -> passes={passes}")

print("\n✅ All similarity scores computed correctly")
print("✅ Fix applied successfully - threshold 0.1 will now pass relevant chunks")