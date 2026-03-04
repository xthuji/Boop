#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_RUNNER="$SCRIPT_DIR/run_tests.py"
PYTHON_PATH="$HOME/miniconda3/envs/python39/bin/python3"

echo "=========================================="
echo "Boop Scripts Test Runner"
echo "=========================================="
echo ""
echo "Running tests using Python test runner..."
echo ""

if [ ! -f "$TEST_RUNNER" ]; then
    echo "❌ Error: Test runner not found at $TEST_RUNNER"
    exit 1
fi

if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Error: Python not found at $PYTHON_PATH"
    echo "Please set the correct Python path in run_tests.sh"
    exit 1
fi

"$PYTHON_PATH" "$TEST_RUNNER" "$@"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Check the results for details."
fi

exit $exit_code
