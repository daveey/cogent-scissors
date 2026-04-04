#!/bin/bash
echo "Testing attempt 012-delta: corner_pressure divisor 8.0→7.0"
echo "Baseline: 9.74 avg (seeds: 9.37, 11.44, 19.86, 2.64, 5.38)"
echo ""
for seed in 42 43 44 45 46; do
  echo "=== Seed $seed ==="
  ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer python3 -m cogames play \
    -m four_score \
    -p class=cvc.cogamer_policy.CvCPolicy \
    -c 32 -r none --seed $seed 2>&1 | grep "per cog" || echo "FAILED seed $seed"
done
