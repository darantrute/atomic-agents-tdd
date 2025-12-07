#!/bin/bash
# run-isolated.sh - Run pipeline in isolated worktree
# Usage: ./run-isolated.sh "Add authentication"

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"feature description\""
    echo "Example: $0 \"Add user authentication\""
    echo ""
    echo "Environment variables:"
    echo "  BASE_BRANCH    - Base branch for feature (default: development)"
    echo "  WORKTREE_BASE  - Directory for worktrees (default: /tmp/tdd-worktrees)"
    exit 1
fi

TASK="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_BASE="${WORKTREE_BASE:-/tmp/tdd-worktrees}"
BASE_BRANCH="${BASE_BRANCH:-development}"

# Create unique worktree name
WORKTREE_NAME="tdd-$(date +%Y%m%d-%H%M%S)-$$"
WORKTREE_PATH="$WORKTREE_BASE/$WORKTREE_NAME"

# Ensure base directory exists
mkdir -p "$WORKTREE_BASE"

# Create worktree with new branch
echo "Creating isolated worktree: $WORKTREE_PATH"
echo "Base branch: $BASE_BRANCH"
# Note: git-setup agent will create the actual feature branch name
# We create a temporary branch here, git-setup will rename it
TEMP_BRANCH="temp-$WORKTREE_NAME"
git worktree add -b "$TEMP_BRANCH" "$WORKTREE_PATH" "$BASE_BRANCH" --quiet

# Change to worktree
cd "$WORKTREE_PATH"

echo ""
echo "Running pipeline in isolated worktree..."
echo "Task: $TASK"
echo "Path: $WORKTREE_PATH"
echo ""

# Run pipeline
python "$SCRIPT_DIR/run.py" "$TASK"

# Store exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    BRANCH=$(git branch --show-current)
    echo "✅ Pipeline completed successfully"
    echo "Branch: $BRANCH (from $BASE_BRANCH)"
    echo ""
    echo "Next steps:"
    echo "  cd $WORKTREE_PATH"
    echo "  git push origin $BRANCH"
    echo ""
    echo "To cleanup this worktree later:"
    echo "  cd $SCRIPT_DIR"
    echo "  git worktree remove $WORKTREE_PATH"
else
    echo "❌ Pipeline failed"
    echo "Worktree preserved for debugging: $WORKTREE_PATH"
fi

exit $EXIT_CODE
