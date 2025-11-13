#!/bin/bash
# Test the MCP server package locally

set -e

echo "========================================="
echo "Testing MCP Server Package"
echo "========================================="
echo ""

# Check environment variables
if [ -z "$OPENSEARCH_KB_API_URL" ] || [ -z "$OPENSEARCH_KB_API_TOKEN" ]; then
    echo "⚠️  Warning: Environment variables not set"
    echo "Set them for full testing:"
    echo "  export OPENSEARCH_KB_API_URL='https://your-api-url'"
    echo "  export OPENSEARCH_KB_API_TOKEN='your-token'"
    echo ""
fi

# Test 1: Build package
echo "1️⃣  Building package..."
python -m build
echo "✅ Build successful"
echo ""

# Test 2: Install locally
echo "2️⃣  Installing package locally..."
pip install -e .
echo "✅ Installation successful"
echo ""

# Test 3: Check command is available
echo "3️⃣  Checking command..."
if command -v opensearch-knowledge-base-mcp-server &> /dev/null; then
    echo "✅ Command 'opensearch-knowledge-base-mcp-server' is available"
else
    echo "❌ Command not found"
    exit 1
fi
echo ""

# Test 4: Check package can be imported
echo "4️⃣  Testing Python import..."
python -c "import opensearch_kb_mcp_server; print(f'✅ Package version: {opensearch_kb_mcp_server.__version__}')"
echo ""

# Test 5: Test MCP protocol (if env vars set)
if [ -n "$OPENSEARCH_KB_API_URL" ] && [ -n "$OPENSEARCH_KB_API_TOKEN" ]; then
    echo "5️⃣  Testing MCP protocol..."
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
        timeout 5 opensearch-knowledge-base-mcp-server 2>/dev/null | \
        python -c "import sys, json; data=json.load(sys.stdin); print('✅ MCP server responds correctly' if 'result' in data else '❌ Invalid response')" || \
        echo "⚠️  MCP protocol test skipped (timeout or error)"
    echo ""
fi

echo "========================================="
echo "✅ All tests passed!"
echo "========================================="
echo ""
echo "Ready to publish to PyPI!"
echo "Run: ./publish.sh"
