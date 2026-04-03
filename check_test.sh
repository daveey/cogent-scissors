#!/bin/bash
# Quick test status check

echo "=== Test Process Status ==="
ps aux | grep "[p]ython3 -m cogames play" | awk '{print "PID", $2, "- CPU:", $9, "- Mem:", $4"%"}'

echo -e "\n=== Test Results (last 20 lines) ==="
tail -20 test_results.txt

echo -e "\n=== Timestamp ==="
date
