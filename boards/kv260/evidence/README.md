# KV260 physical-evidence staging

This directory is a **local staging area** for Physical Lab evidence. Generated logs, screenshots, manifests, and hardware measurements are ignored by Git by default so the source tree does not accidentally accumulate machine-specific or bulky artifacts.

For each physical checkpoint:

1. copy `manifest.example.json` to a lab/date-specific filename;
2. fill the fields from the actual run;
3. keep the named logs next to that manifest;
4. attach/publish the evidence through the project's hardware-checkpoint record when the run is formally accepted.

Do not change `PASS`/evidence fields to make a failed run look successful. A cloud-CI run is not a substitute for a real KV260 checkpoint.

The template itself is version-controlled; generated evidence is not automatically committed.
