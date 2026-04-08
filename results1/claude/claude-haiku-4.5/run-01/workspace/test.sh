#!/bin/bash
# Test script for Prompt Optimizer

echo "=== Test 1: Basic file analysis ==="
python3 prompt_optimizer.py example_prompt.txt
echo ""

echo "=== Test 2: Verbose mode (with token savings per suggestion) ==="
python3 prompt_optimizer.py example_prompt.txt --verbose
echo ""

echo "=== Test 3: Stdin analysis ==="
echo "Well, basically this is quite very redundant text that is essentially unnecessary to read carefully." | python3 prompt_optimizer.py -
echo ""

echo "=== Test 4: Already optimized text ==="
echo "Check if a number is prime by testing divisors." | python3 prompt_optimizer.py -
