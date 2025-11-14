"""Setup module to configure Python path for scripts."""
import os
import sys

# Add project root to Python path (always at the beginning)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Remove any existing instances of project_root from sys.path
while project_root in sys.path:
    sys.path.remove(project_root)

# Insert at the very beginning to ensure local version takes precedence
sys.path.insert(0, project_root)

print(f"Using local batem from: {project_root}")
