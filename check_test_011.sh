#!/bin/bash
echo "=== Attempt 011: RETREAT_MARGIN 15→20 ===" 
ps aux | grep "[p]ython3 -m cogames play" | awk '{print "PID", $2, "- Started:", $9, "- CPU:", $10}'
echo ""
echo "=== Results so far ===" 
tail -30 test_results_011.txt
echo ""
echo "=== Timestamp ===" 
date
