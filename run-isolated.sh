#!/bin/bash
# run-isolated.sh - Run pipeline in isolated worktree
# Usage: ./run-isolated.sh "Add authentication"
#    OR: ./run-isolated.sh spec-file.txt (auto-detects and reads file)
#    OR: ./run-isolated.sh --continue (resume most recent worktree)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_BASE="${WORKTREE_BASE:-/tmp/tdd-worktrees}"
BASE_BRANCH="${BASE_BRANCH:-development}"

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"feature description\" OR $0 spec-file.txt OR $0 --continue"
    echo ""
    echo "Examples:"
    echo "  $0 \"Add user authentication\""
    echo "  $0 \"$(cat spec.txt)\"             # Read file content"
    echo "  $0 spec.txt                       # Auto-detects file and reads it"
    echo "  $0 --continue                     # Resume most recent worktree"
    echo ""
    echo "Environment variables:"
    echo "  BASE_BRANCH    - Base branch for feature (default: development)"
    echo "  WORKTREE_BASE  - Directory for worktrees (default: /tmp/tdd-worktrees)"
    exit 1
fi

# Check for --continue mode
if [ "$1" = "--continue" ]; then
    echo "🔄 Continue mode: Finding most recent worktree..."
    echo ""

    # Find most recent worktree
    LATEST_WORKTREE=$(ls -td "$WORKTREE_BASE"/tdd-* 2>/dev/null | head -1)

    if [ -z "$LATEST_WORKTREE" ]; then
        echo "❌ No existing worktree found"
        echo "   Expected location: $WORKTREE_BASE/tdd-*"
        echo ""
        echo "Available worktrees:"
        ls -1 "$WORKTREE_BASE" 2>/dev/null || echo "  (none)"
        exit 1
    fi

    echo "📂 Found worktree: $(basename "$LATEST_WORKTREE")"
    echo "   Path: $LATEST_WORKTREE"
    echo ""

    # Change to worktree
    cd "$LATEST_WORKTREE"

    # Validate state
    if [ ! -f progress.txt ]; then
        echo "⚠️  Warning: No progress.txt found"
        echo "   This worktree may not have a valid pipeline state"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # Show progress summary
    if [ -f progress.txt ]; then
        echo "📊 Previous progress:"
        cat progress.txt | tail -10
        echo ""
    fi

    # Count tests
    if ls specs/chore-*-tests.json 1> /dev/null 2>&1; then
        TESTS_FILE=$(ls specs/chore-*-tests.json | head -1)
        TOTAL_TESTS=$(cat "$TESTS_FILE" | jq 'length' 2>/dev/null || echo "?")
        PASSING_TESTS=$(cat "$TESTS_FILE" | grep -c '"passes": true' 2>/dev/null || echo "0")
        FAILING_TESTS=$((TOTAL_TESTS - PASSING_TESTS))

        echo "   Total tests: $TOTAL_TESTS"
        echo "   Completed: $PASSING_TESTS"
        echo "   Remaining: $FAILING_TESTS"
        echo ""
    fi

    # Run continuation
    echo "🚀 Running continuation agent..."
    echo ""
    python "$SCRIPT_DIR/run.py" --continue --project-dir .

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        BRANCH=$(git branch --show-current)
        echo ""
        echo "✅ Continuation completed successfully"
        echo "   Branch: $BRANCH"
        echo "   Path: $LATEST_WORKTREE"
    else
        echo ""
        echo "❌ Continuation failed"
        echo "   Check logs above for errors"
    fi

    exit $EXIT_CODE
fi

INPUT="$1"

# Auto-detect if input is a file path and read it
if [ -f "$INPUT" ]; then
    echo "📄 Detected file: $INPUT"
    echo "   Reading file contents..."
    TASK=$(cat "$INPUT")
    echo "   ✅ Loaded ${#TASK} characters from file"
    echo ""
elif [ ${#INPUT} -lt 50 ]; then
    # Input is very short - likely a mistake
    echo "⚠️  WARNING: Input is very short (${#INPUT} characters)"
    echo ""
    echo "If '$INPUT' is a filename, make sure:"
    echo "  1. The file exists in the current directory"
    echo "  2. Or use: $0 \"\$(cat $INPUT)\""
    echo ""
    read -p "Continue with this short input? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    TASK="$INPUT"
else
    TASK="$INPUT"
fi

# Validate input looks like a specification
if [ ${#TASK} -gt 100 ]; then
    # Only validate structure for substantial inputs
    if ! echo "$TASK" | grep -qi "STACK\|FEATURES\|DATABASE\|PROJECT\|TYPE"; then
        echo "⚠️  WARNING: Input doesn't look like a specification"
        echo "   Expected sections: PROJECT, STACK, FEATURES, DATABASE, etc."
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 1
        fi
    fi
fi

# Create human-readable worktree name from task description
# Extract first line or PROJECT name if available, limit to 40 chars
TASK_SLUG=$(echo "$TASK" | grep -i "^PROJECT:" | head -1 | sed 's/PROJECT://i' | xargs || echo "$TASK" | head -1)
TASK_SLUG=$(echo "$TASK_SLUG" | head -c 40 | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g' | sed 's/--*/-/g' | sed 's/^-\|-$//g' | tr -d '\n')

# Fallback to 'task' if slug is empty
TASK_SLUG="${TASK_SLUG:-task}"

WORKTREE_NAME="tdd-${TASK_SLUG}-$(date +%Y%m%d-%H%M)"
WORKTREE_PATH="$WORKTREE_BASE/$WORKTREE_NAME"

# Ensure base directory exists
mkdir -p "$WORKTREE_BASE"

# Create worktree with new branch
echo "🔧 Creating isolated worktree..."
echo "   Name: $WORKTREE_NAME"
echo "   Path: $WORKTREE_PATH"
echo "   Base: $BASE_BRANCH"
echo ""

# Note: git-setup agent will create the actual feature branch name
# We create a temporary branch here, git-setup will rename it
TEMP_BRANCH="temp-$WORKTREE_NAME"
git worktree add -b "$TEMP_BRANCH" "$WORKTREE_PATH" "$BASE_BRANCH" --quiet

# Change to worktree
cd "$WORKTREE_PATH"

echo "🚀 Running TDD pipeline..."
echo "   Task: ${TASK:0:80}$([ ${#TASK} -gt 80 ] && echo '...')"
echo "   Spec length: ${#TASK} characters"
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
