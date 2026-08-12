# Verification records

This directory binds publication review to exact content.

- `documentation-review.json` records the Hesperos customer-journey review.
- `accessibility-review.json` records the separate accessibility review.
- `adversarial-verification.json` records the separate TestForge challenge pass.
- `live-verification.json` is created only after the reviewed commit is published, GitHub Pages has rebuilt, and the live repository, routes, navigation, metadata, custom 404, and assets have been rechecked.

Candidate reviews bind to an exact content fingerprint covering customer-facing documentation, Pages source, and final visual assets. Any content change after review invalidates the old receipts. The live receipt additionally binds to the final public commit and deployment run.

A receipt reports only its named checks. It does not establish fresh-host installation, host discovery, host invocation, live table quality, balance, rules accuracy, VTT compatibility, originality, rights clearance, or semantic spoiler safety unless those observations are explicitly recorded.