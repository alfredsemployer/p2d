# p2d v0.3 offline evaluation

- Artifact: `p2d:20260723-kimi-k3-v02:v0.3-migration`
- Contract checks: 12/12
- Formal solver regressions: 3/3
- Overall pass: `true`

## Limits

- These checks validate contracts and deterministic behavior, not world truth.
- Legacy migration valences remain uncalibrated pending external labels.
- The Kimi graph contains no suitable strict empirical inference, so its solver coverage is correctly zero.
