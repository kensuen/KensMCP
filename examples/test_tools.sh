#!/bin/bash
# KensMCP Tool Testing Script
# Run: ./examples/test_tools.sh

BASE_URL="http://localhost:8080"

echo "======================================"
echo "⚡ KensMCP Tool Tests"
echo "======================================"
echo ""

# Health check
echo "🏥 Health Check:"
curl -s "$BASE_URL/health" | jq .
echo ""

# List tools
echo "🔧 Available Tools:"
curl -s "$BASE_URL/tools" | jq '.tools[].name'
echo ""

# Calculator
echo "🔢 Calculator Test:"
curl -s -X POST "$BASE_URL/tools/calculate" \
  -H "Content-Type: application/json" \
  -d '{"expression": "sqrt(256) + 10"}' | jq .
echo ""

# Text Transform
echo "📝 Text Transform Test:"
curl -s -X POST "$BASE_URL/tools/text_transform" \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "operation": "uppercase"}' | jq .
echo ""

# System Info
echo "💻 System Info Test:"
curl -s -X POST "$BASE_URL/tools/system_info" \
  -H "Content-Type: application/json" \
  -d '{"info_type": "time"}' | jq .
echo ""

# UUID Generator
echo "🆔 UUID Generator Test:"
curl -s -X POST "$BASE_URL/tools/generate_uuid" \
  -H "Content-Type: application/json" \
  -d '{"count": 2}' | jq .
echo ""

# Hash Generator
echo "🔐 Hash Generator Test:"
curl -s -X POST "$BASE_URL/tools/generate_hash" \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "algorithm": "sha256"}' | jq .
echo ""

# Base64
echo "🔤 Base64 Test:"
curl -s -X POST "$BASE_URL/tools/base64_convert" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "operation": "encode"}' | jq .
echo ""

# JSON Formatter
echo "📋 JSON Formatter Test:"
curl -s -X POST "$BASE_URL/tools/json_format" \
  -H "Content-Type: application/json" \
  -d '{"json_string": "{\"a\":1,\"b\":2}", "operation": "format"}' | jq .
echo ""

# Notes - Create
echo "📒 Note Create Test:"
curl -s -X POST "$BASE_URL/tools/note_create" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Note", "content": "This is a test note!"}' | jq .
echo ""

# Notes - List
echo "📒 Note List Test:"
curl -s -X POST "$BASE_URL/tools/note_list" \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
echo ""

echo "======================================"
echo "✅ All tests complete!"
echo "======================================"

