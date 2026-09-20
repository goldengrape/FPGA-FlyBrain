# KV260 physical-evidence staging

This directory is a **local staging area** for Physical Lab evidence. Generated logs, screenshots, manifests, and hardware measurements are ignored by Git by default so the source tree does not accidentally accumulate machine-specific or bulky artifacts.

For each physical checkpoint:

1. copy `manifest.example.json` to a lab/date-specific filename;
2. fill every applicable explicit field from the actual run;
3. use `null`, an empty object/list, or a short "not applicable" explanation when a field truly does not apply — do not silently omit required evidence;
4. keep the named logs/reports/photos next to that manifest;
5. attach/publish the evidence through the project's hardware-checkpoint record when the run is formally accepted.

The explicit fields mirror T-HW-011: Git commit, board/revision, development-host OS, Vivado version, board/platform version when known, Linux-image version when relevant, bitstream/build hashes when relevant, test input, output summary, hardware target/device identity, artifact paths, and date.

Do not change `PASS`/evidence fields to make a failed run look successful. A cloud-CI run is not a substitute for a real KV260 checkpoint.

The template itself is version-controlled; generated evidence is not automatically committed.
