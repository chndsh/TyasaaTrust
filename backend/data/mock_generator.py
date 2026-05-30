"""Stub for seeding development data into the database."""

import os
import sys

# Compute the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if os.path.basename(project_root) == "backend":
    sys.path.remove(project_root)
    project_root = os.path.dirname(project_root)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

if __name__ == "__main__":
    print("Mock generator stub: add seed logic here when ready.")
