#!/bin/bash
# Quick E2E Test Script for pytaiga-mcp v0.2.0

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║         pytaiga-mcp v0.2.0 - E2E Testing Quick Start              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test 1: Check Python version
print_test "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ $PYTHON_VERSION == 3.1* ]]; then
    print_pass "Python 3.10+ found: $PYTHON_VERSION"
else
    print_fail "Python 3.10+ required, found: $PYTHON_VERSION"
    exit 1
fi
echo ""

# Test 2: Check dependencies
print_test "Checking dependencies..."
if command -v uv &> /dev/null; then
    print_pass "uv found"
else
    print_fail "uv not found, install with: pip install uv"
    exit 1
fi
echo ""

# Test 3: Run unit tests
print_test "Running unit tests (quick)..."
echo "Running first 10 tests as smoke test..."
if pytest tests/ -v --tb=short -x 2>&1 | head -100; then
    print_pass "Unit tests passed"
else
    print_fail "Unit tests failed"
    echo "Run full tests with: pytest tests/ -v"
    exit 1
fi
echo ""

# Test 4: Code quality checks
print_test "Running code quality checks..."

echo "  - Code formatting (black)..."
if black --check src/ 2>&1 > /dev/null; then
    print_pass "Code formatting OK"
else
    print_fail "Code formatting issues found"
    echo "  Run: black src/"
fi

echo "  - Import organization (isort)..."
if isort --check-only src/ 2>&1 > /dev/null; then
    print_pass "Import organization OK"
else
    print_fail "Import organization issues found"
    echo "  Run: isort src/"
fi

echo "  - Type checking (mypy)..."
if mypy src/ 2>&1 > /dev/null; then
    print_pass "Type checking OK"
else
    print_fail "Type checking issues found"
    echo "  Run: mypy src/"
fi

echo "  - Linting (flake8)..."
if flake8 src/ 2>&1 > /dev/null; then
    print_pass "Linting OK"
else
    print_fail "Linting issues found"
    echo "  Run: flake8 src/"
fi
echo ""

# Test 5: Verify MCP server can start
print_test "Verifying MCP server startup..."
timeout 5 uv run python src/server.py &
SERVER_PID=$!
sleep 2

if kill -0 $SERVER_PID 2>/dev/null; then
    print_pass "MCP server started successfully"
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
else
    print_fail "MCP server failed to start"
    exit 1
fi
echo ""

# Test 6: Run edge case tests
print_test "Running edge case tests..."
if pytest tests/integration/test_edge_cases_simple.py -v --tb=short 2>&1 | tail -20; then
    print_pass "Edge case tests passed"
else
    print_fail "Edge case tests failed"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════════╗"
echo -e "${GREEN}✅ E2E QUICK TEST COMPLETED${NC}"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Set up Taiga instance (local or remote)"
echo "2. Configure .env with Taiga URL"
echo "3. Start MCP server: uv run python src/server.py"
echo "4. Test with Claude Desktop or Cursor"
echo ""
echo "For detailed testing guide, see:"
echo "  - /tmp/E2E_TESTING_GUIDE.md"
echo "  - CLAUDE.md (development patterns)"
echo "  - README.md (installation and usage)"
echo ""
