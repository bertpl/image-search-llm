
#!/bin/bash
# ==================================================================================
#  Tag or search images using LLMs; run 'image_search.sh [--help]' for help.
# ==================================================================================

# --- activate conda environment ---
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate image-search-llm  # UPDATE TO YOUR ENVIRONMENT NAME

# --- run image_search.py with absolute path ---
SCRIPT_DIR=$(realpath "$(dirname "$0")")
python "$SCRIPT_DIR/image_search.py" "$@"