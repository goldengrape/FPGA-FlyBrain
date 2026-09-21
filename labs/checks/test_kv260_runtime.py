"""Host-side contract tests for KV260 LAB-HW-05/06 runtime helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "boards" / "kv260" / "runtime"
HASH_IMAGE = RUNTIME / "hash_image.py"
IMAGE_MANIFEST = RUNTIME / "ubuntu24_image.json"
COLLECT_BOOT_INFO = RUNTIME / "collect_boot_info.sh"
LOOPBACK = RUNTIME / "loopback_mmio.py"
STATE_BRAM = RUNTIME / "state_bram_mmio.py"
REPLAY_REF = RUNTIME / "lab08_replay_reference.py"
REPLAY_CHECKER = RUNTIME / "small_replay_mmio.py"
REPLAY_FIXTURE = ROOT / "boards" / "kv260" / "fixtures" / "lab08_four_neuron_replay_v1.json"
DDR_INTEGRITY = RUNTIME / "ddr_integrity.py"
AXI_CDMA_BENCH = RUNTIME / "axi_cdma_benchmark.py"
UDMABUF_PREFLIGHT = RUNTIME / "preflight_udmabuf.py"
UDMABUF_SOURCE = RUNTIME / "udmabuf_source.json"


def test_image_manifest_freezes_identity_without_inventing_checksum():
    manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == "AUTHORING_CANDIDATE"
    assert manifest["distribution"] == "Ubuntu Server 24.04 LTS"
    assert "KV260" in manifest["target"]
    assert manifest["image_filename"].endswith("20250423.img.xz")
    assert manifest["source_page"] == "https://ubuntu.com/download/amd"
    assert manifest["expected_sha256"] is None
    assert manifest["formal_hash_pass_blocked"] is True


def test_hash_image_records_but_does_not_fake_expected_hash(tmp_path):
    manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    image = tmp_path / manifest["image_filename"]
    image.write_bytes(b"fpga-flybrain-test-image")

    result = subprocess.run(
        [sys.executable, str(HASH_IMAGE), str(image)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-05" in result.stdout
    assert "IMAGE_SHA256=" in result.stdout
    assert "EXPECTED_SHA256=UNSET" in result.stdout
    assert "STATUS=RECORDED_UNVERIFIED" in result.stdout
    assert "STATUS=PASS" not in result.stdout


def test_hash_image_can_enforce_frozen_hash(tmp_path):
    manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    image = tmp_path / manifest["image_filename"]
    image.write_bytes(b"known")

    expected = hashlib.sha256(b"known").hexdigest()
    manifest["expected_sha256"] = expected
    local_manifest = tmp_path / "manifest.json"
    local_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(HASH_IMAGE),
            str(image),
            "--manifest",
            str(local_manifest),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert f"EXPECTED_SHA256={expected}" in result.stdout
    assert "STATUS=PASS" in result.stdout


def test_hash_image_rejects_wrong_filename(tmp_path):
    image = tmp_path / "wrong.img.xz"
    image.write_bytes(b"wrong")
    result = subprocess.run(
        [sys.executable, str(HASH_IMAGE), str(image)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 3
    assert "ERROR=IMAGE_FILENAME_MISMATCH" in result.stdout


def test_collect_boot_info_shell_syntax_and_contract():
    result = subprocess.run(
        ["bash", "-n", str(COLLECT_BOOT_INFO)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    text = COLLECT_BOOT_INFO.read_text(encoding="utf-8")
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-05" in text
    assert "uname -a" in text
    assert "/etc/os-release" in text
    assert "/proc/device-tree/model" in text
    assert "xmutil boardid" in text
    assert "xmutil bootfw_status" in text



def test_loopback_dry_run_is_self_checking_and_writes_trace(tmp_path):
    trace = tmp_path / "lab-hw-06-trace.json"
    result = subprocess.run(
        [
            sys.executable,
            str(LOOPBACK),
            "--dry-run",
            "--json-out",
            str(trace),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-06" in result.stdout
    assert "mmio_base=0xa0010000" in result.stdout.lower()
    assert "TRANSPORT=DRY_RUN_MODEL" in result.stdout
    assert "SAMPLE_COUNT=12" in result.stdout
    assert "STATUS=PASS" in result.stdout

    payload = json.loads(trace.read_text(encoding="utf-8"))
    assert payload["lab_id"] == "LAB-HW-06"
    assert payload["base"] == 0xA0010000
    assert payload["gpio_data_offset"] == 0
    assert payload["gpio2_data_offset"] == 8
    assert payload["rounds"] == 2
    assert len(payload["trace"]) == 12
    assert payload["trace"][-1]["write"] == 0xFFFFFFFF
    assert payload["trace"][-1]["read"] == 0


def test_loopback_rejects_invalid_round_count():
    result = subprocess.run(
        [sys.executable, str(LOOPBACK), "--dry-run", "--rounds", "0"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert "ERROR=INVALID_ROUND_COUNT" in result.stdout


def test_loopback_reports_missing_transport_before_mapping(tmp_path):
    missing = tmp_path / "no-dev-mem"
    result = subprocess.run(
        [sys.executable, str(LOOPBACK), "--device", str(missing)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 3
    assert "ERROR=TRANSPORT_DEVICE_MISSING" in result.stdout


def test_loopback_cli_does_not_expose_arbitrary_physical_base():
    text = LOOPBACK.read_text(encoding="utf-8")
    assert 'MMIO_BASE = 0xA0010000' in text
    assert 'parser.add_argument("--base"' not in text
    assert "TRANSPORT_REQUIRES_ROOT" in text



def test_state_bram_dry_run_checks_multiple_addresses_and_rewrite(tmp_path):
    trace = tmp_path / "lab-hw-07-trace.json"
    result = subprocess.run(
        [
            sys.executable,
            str(STATE_BRAM),
            "--dry-run",
            "--json-out",
            str(trace),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-07" in result.stdout
    assert "state_base=0xa0000000" in result.stdout.lower()
    assert "STATE_WORDS=1024" in result.stdout
    assert "STATE_BYTES=4096" in result.stdout
    assert "TRANSPORT=DRY_RUN_MODEL" in result.stdout
    assert "CHECKED_READS=14" in result.stdout
    assert "STATUS=PASS" in result.stdout

    payload = json.loads(trace.read_text(encoding="utf-8"))
    assert payload["lab_id"] == "LAB-HW-07"
    assert payload["state_base"] == 0xA0000000
    assert payload["state_words"] == 1024
    assert payload["state_bytes"] == 4096
    assert len(payload["trace"]) == 14
    final = {
        row["index"]: row["read"]
        for row in payload["trace"]
        if row["phase"] == "REWRITE_PRESERVATION"
    }
    assert final[1] == 0x01020304
    assert final[511] == 0xCAFEBABE
    assert final[7] == 0x55667788
    assert final[1023] == 0xFFFFFFFF


def test_state_bram_reports_missing_transport_before_mapping(tmp_path):
    missing = tmp_path / "no-dev-mem"
    result = subprocess.run(
        [sys.executable, str(STATE_BRAM), "--device", str(missing)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 3
    assert "ERROR=TRANSPORT_DEVICE_MISSING" in result.stdout


def test_state_bram_cli_freezes_window_and_no_arbitrary_base():
    text = STATE_BRAM.read_text(encoding="utf-8")
    assert "STATE_BASE = 0xA0000000" in text
    assert "STATE_WORDS = 1024" in text
    assert 'parser.add_argument("--base"' not in text
    assert "TRANSPORT_REQUIRES_ROOT" in text
    assert "STATE_READBACK_OR_ALIAS_MISMATCH" in text



def test_lab08_fixture_matches_lesson12_teaching_network():
    fixture = json.loads(REPLAY_FIXTURE.read_text(encoding="utf-8"))
    assert fixture["fixture_id"] == "lesson12_four_neuron_replay_v1"
    assert fixture["model"]["kind"] == "teaching_event_machine"
    assert fixture["model"]["stochastic"] is False
    assert fixture["network"]["source_index"] == [[0, 2], [2, 1], [3, 1], [4, 0]]
    assert fixture["network"]["records"] == [
        {"target": 1, "weight": 2},
        {"target": 2, "weight": 1},
        {"target": 3, "weight": 2},
        {"target": 3, "weight": 1},
    ]
    assert fixture["network"]["thresholds"] == [99, 2, 1, 3]
    assert fixture["input"]["initial_state"] == [0, 0, 0, 0]
    assert fixture["input"]["initial_queue"] == [0]


def test_lab08_reference_reproduces_lesson12_trace(tmp_path):
    out = tmp_path / "reference.json"
    result = subprocess.run(
        [sys.executable, str(REPLAY_REF), "--fixture", str(REPLAY_FIXTURE), "--json-out", str(out)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "SPIKE_ORDER=0,1,2,3" in result.stdout
    assert "FINAL_STATE=0,0,0,0" in result.stdout
    for word in ("0x01020201", "0x02010101", "0x13020200", "0x23010301"):
        assert f"WORD={word}" in result.stdout
    assert "STATUS=PASS" in result.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["spike_order"] == [0, 1, 2, 3]
    assert payload["event_words"] == [0x01020201, 0x02010101, 0x13020200, 0x23010301]
    assert payload["final_state"] == [0, 0, 0, 0]


def test_lab08_checker_dry_run_is_full_differential(tmp_path):
    out = tmp_path / "dry-run.json"
    result = subprocess.run(
        [sys.executable, str(REPLAY_CHECKER), "--fixture", str(REPLAY_FIXTURE), "--dry-run", "--json-out", str(out)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-08" in result.stdout
    assert "TRANSPORT=DRY_RUN_REPLAY_MODEL" in result.stdout
    assert "EXPECTED_SPIKES=0,1,2,3" in result.stdout
    assert "OBSERVED_SPIKES=0,1,2,3" in result.stdout
    assert "DIFFERENTIAL=PASS" in result.stdout
    assert "STATUS=PASS" in result.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["lab_id"] == "LAB-HW-08"
    assert payload["state_base"] == 0xA0000000
    assert payload["control_base"] == 0xA0010000
    assert payload["expected"]["event_words"] == payload["observed"]["event_words"]
    assert payload["differential_errors"] == []


def test_lab08_checker_reports_missing_transport_before_mapping(tmp_path):
    missing = tmp_path / "no-dev-mem"
    result = subprocess.run(
        [sys.executable, str(REPLAY_CHECKER), "--fixture", str(REPLAY_FIXTURE), "--device", str(missing)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 4
    assert "ERROR=TRANSPORT_DEVICE_MISSING" in result.stdout


def test_lab08_checker_freezes_addresses_and_no_arbitrary_base():
    text = REPLAY_CHECKER.read_text(encoding="utf-8")
    assert "STATE_BASE = 0xA0000000" in text
    assert "GPIO_BASE = 0xA0010000" in text
    assert 'parser.add_argument("--base"' not in text
    assert "ENGINE_ALREADY_BUSY" in text
    assert "ENGINE_TIMEOUT" in text
    assert "REPLAY_DIFFERENTIAL_MISMATCH" in text



def test_lab09_ddr_integrity_dry_run_passes_and_records_scope(tmp_path):
    out = tmp_path / "lab-hw-09-dry-run.json"
    result = subprocess.run(
        [sys.executable, str(DDR_INTEGRITY), "--dry-run", "--json-out", str(out)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-09" in result.stdout
    assert "MODE=DRY_RUN_HOST_MEMORY_MODEL" in result.stdout
    assert "TEST_BYTES=4194304" in result.stdout
    assert "CHUNK_BYTES=1048576" in result.stdout
    assert "CHUNK_COUNT=4" in result.stdout
    assert "INTEGRITY=PASS" in result.stdout
    assert "PERFORMANCE_BLOCKED=0" in result.stdout
    assert "HOST_PATH_WRITE_MIB_PER_S=" in result.stdout
    assert "HOST_PATH_READ_MIB_PER_S=" in result.stdout
    assert "BANDWIDTH_SCOPE=HOST_PATH_OBSERVATION_NOT_PEAK_DDR_OR_PL_AXI" in result.stdout
    assert "STATUS=PASS" in result.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["lab_id"] == "LAB-HW-09"
    assert payload["byte_count"] == 4 * 1024 * 1024
    assert payload["chunk_bytes"] == 1024 * 1024
    assert payload["integrity_pass"] is True
    assert payload["performance_blocked"] is False
    assert payload["expected_sha256"] == payload["observed_sha256"]


def test_lab09_corruption_blocks_performance_claims(tmp_path):
    out = tmp_path / "corrupt.json"
    result = subprocess.run(
        [sys.executable, str(DDR_INTEGRITY), "--dry-run", "--inject-corruption-for-test", "--json-out", str(out)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 6
    assert "INTEGRITY=FAIL" in result.stdout
    assert "PERFORMANCE_BLOCKED=1" in result.stdout
    assert "ERROR=DDR_INTEGRITY_MISMATCH" in result.stdout
    assert "HOST_PATH_WRITE_MIB_PER_S=" not in result.stdout
    assert "HOST_PATH_READ_MIB_PER_S=" not in result.stdout
    assert "STATUS=FAIL" in result.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["integrity_pass"] is False
    assert payload["performance_blocked"] is True
    assert payload["mismatch"] is not None


def test_lab09_physical_injection_is_rejected():
    result = subprocess.run(
        [sys.executable, str(DDR_INTEGRITY), "--physical", "--inject-corruption-for-test"],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 2
    assert "ERROR=INJECTION_NOT_ALLOWED_PHYSICAL" in result.stdout


def test_lab09_helper_freezes_geometry_and_avoids_raw_physical_ddr():
    text = DDR_INTEGRITY.read_text(encoding="utf-8")
    assert "PHYSICAL_BYTES = 64 * 1024 * 1024" in text
    assert "CHUNK_BYTES = 1 * 1024 * 1024" in text
    assert "PAYLOAD_ID = \"shake256-chunk-index-v1\"" in text
    assert 'parser.add_argument("--bytes"' not in text
    assert 'Path("/dev/mem")' not in text
    assert "NOT_KV260_RUNTIME_ENVIRONMENT" in text
    assert "BANDWIDTH_SCOPE=HOST_PATH_OBSERVATION_NOT_PEAK_DDR_OR_PL_AXI" in text



def test_lab10_axi_cdma_dry_run_is_stable_and_retains_raw_samples(tmp_path):
    out = tmp_path / "lab-hw-10-dry-run.json"
    result = subprocess.run(
        [sys.executable, str(AXI_CDMA_BENCH), "--dry-run", "--json-out", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-10" in result.stdout
    assert "MODE=DRY_RUN_CDMA_MODEL" in result.stdout
    assert "CDMA_CONTROL_BASE=0xa0020000" in result.stdout
    assert "PL_DDR_PORT=S_AXI_HP0_FPD" in result.stdout
    assert "PL_DDR_COHERENCY=NON_COHERENT" in result.stdout
    assert "PAYLOAD_BYTES=262144" in result.stdout
    assert "SMALL_BLOCK_BYTES=256" in result.stdout
    assert "SMALL_BLOCK_COUNT=1024" in result.stdout
    assert "WARMUP_RUNS=5" in result.stdout
    assert "MEASURED_RUNS=20" in result.stdout
    assert "BATCH_COUNT=2" in result.stdout
    assert "PRECHECK_INTEGRITY=PASS" in result.stdout
    assert "MEASUREMENT_STABLE=1" in result.stdout
    assert "PERFORMANCE_CONCLUSION_ALLOWED=1" in result.stdout
    assert "SCATTERED_TO_CONTIGUOUS_MEDIAN_TIME_RATIO=" in result.stdout
    assert "STATUS=PASS" in result.stdout

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["lab_id"] == "LAB-HW-10"
    assert payload["integrity_pass"] is True
    assert payload["measurement_stable"] is True
    assert payload["performance_conclusion_allowed"] is True
    assert payload["workload"]["payload_bytes"] == 256 * 1024
    assert payload["workload"]["warmup_runs"] == 5
    assert payload["workload"]["measured_runs"] == 20
    assert payload["workload"]["batch_count"] == 2
    for pattern in ("contiguous", "scattered"):
        assert len(payload["patterns"][pattern]) == 2
        for batch in payload["patterns"][pattern]:
            assert len(batch["samples_ns"]) == 20
            assert batch["min_ns"] <= batch["median_ns"] <= batch["max_ns"]
        assert payload["stability_pct"][pattern] <= 10.0


def test_lab10_corruption_blocks_benchmark_conclusion(tmp_path):
    out = tmp_path / "corrupt.json"
    result = subprocess.run(
        [
            sys.executable,
            str(AXI_CDMA_BENCH),
            "--dry-run",
            "--inject-corruption-for-test",
            "--json-out",
            str(out),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 5
    assert "ERROR=BENCHMARK_INTEGRITY_MISMATCH" in result.stdout
    assert "PERFORMANCE_CONCLUSION_ALLOWED=0" in result.stdout
    assert "SCATTERED_TO_CONTIGUOUS_MEDIAN_TIME_RATIO=" not in result.stdout
    assert "STATUS=FAIL" in result.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["integrity_pass"] is False
    assert payload["performance_conclusion_allowed"] is False


def test_lab10_instability_blocks_benchmark_conclusion(tmp_path):
    out = tmp_path / "unstable.json"
    result = subprocess.run(
        [
            sys.executable,
            str(AXI_CDMA_BENCH),
            "--dry-run",
            "--unstable-for-test",
            "--json-out",
            str(out),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 7
    assert "ERROR=MEASUREMENT_UNSTABLE" in result.stdout
    assert "MEASUREMENT_STABLE=0" in result.stdout
    assert "PERFORMANCE_CONCLUSION_ALLOWED=0" in result.stdout
    assert "SCATTERED_TO_CONTIGUOUS_MEDIAN_TIME_RATIO=" not in result.stdout
    assert "STATUS=FAIL" in result.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["measurement_stable"] is False
    assert payload["performance_conclusion_allowed"] is False
    assert payload["stability_pct"]["scattered"] > 10.0


def test_lab10_physical_test_injection_is_rejected():
    result = subprocess.run(
        [sys.executable, str(AXI_CDMA_BENCH), "--physical", "--unstable-for-test"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 3
    assert "ERROR=TEST_INJECTION_NOT_ALLOWED_PHYSICAL" in result.stdout


def test_lab10_helper_freezes_dma_buffer_workload_and_control_contract():
    source = AXI_CDMA_BENCH.read_text(encoding="utf-8")
    assert "CDMA_BASE = 0xA0020000" in source
    assert "DMA_BUFFER_MIN_BYTES = 2 * 1024 * 1024" in source
    assert "DST_OFFSET = 1 * 1024 * 1024" in source
    assert "PAYLOAD_BYTES = 256 * 1024" in source
    assert "SMALL_BLOCK_BYTES = 256" in source
    assert "WARMUP_RUNS = 5" in source
    assert "MEASURED_RUNS = 20" in source
    assert "STABILITY_LIMIT_PCT = 10.0" in source
    assert "HP0_DDR_LOW_END = 0x80000000" in source
    assert 'Path("/dev/udmabuf0")' in source
    assert 'Path("/sys/class/u-dma-buf/udmabuf0")' in source
    assert 'Path("/dev/mem")' in source
    assert 'getattr(os, "O_SYNC", 0)' in source
    assert "DMA_BUFFER_OUTSIDE_HP0_DDR_LOW" in source
    assert "DMA_BUFFER_SYNC_MODE_MISSING" in source
    assert "DMA_BUFFER_UNSAFE_SYNC_MODE" in source
    assert 'sync_mode not in (1, 2)' in source
    assert "CDMA_TIMEOUT" in source
    assert "BENCHMARK_INTEGRITY_MISMATCH" in source
    assert "MEASUREMENT_UNSTABLE" in source
    assert 'parser.add_argument("--base"' not in source
    assert 'parser.add_argument("--payload-bytes"' not in source



def test_lab10_udmabuf_source_manifest_is_pinned_and_still_candidate():
    manifest = json.loads(UDMABUF_SOURCE.read_text(encoding="utf-8"))
    assert manifest["status"] == "AUTHORING_CANDIDATE"
    assert manifest["provider"] == "u-dma-buf"
    assert manifest["upstream_commit"] == "15bcde3cb960321e99983e227aeacc5807888333"
    assert manifest["driver_version"] == "5.5.0"
    assert manifest["buffer_bytes"] == 4 * 1024 * 1024
    assert manifest["minimum_lab10_bytes"] == 2 * 1024 * 1024
    assert manifest["required_open_mode"] == "O_RDWR|O_SYNC"
    assert manifest["allowed_sync_modes"] == [1, 2]
    assert manifest["physical_validation"] == "PENDING_REAL_KV260"


def test_lab10_udmabuf_preflight_dry_run_records_full_contract(tmp_path):
    out = tmp_path / "udmabuf-preflight.json"
    result = subprocess.run(
        [
            sys.executable,
            str(UDMABUF_PREFLIGHT),
            "--dry-run",
            "--json-out",
            str(out),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "FPGA_FLYBRAIN_LAB=LAB-HW-10-PREREQ" in result.stdout
    assert "MODE=DRY_RUN_PREFLIGHT_MODEL" in result.stdout
    assert "EXPECTED_UDMABUF_COMMIT=15bcde3cb960321e99983e227aeacc5807888333" in result.stdout
    assert "DMA_BUFFER_MIN_BYTES=2097152" in result.stdout
    assert "COURSE_BUFFER_BYTES=4194304" in result.stdout
    assert "DMA_BUFFER_SYNC_MODE=1" in result.stdout
    assert "DMA_BUFFER_OPEN_FLAGS=O_RDWR|O_SYNC" in result.stdout
    assert "STATUS=PASS" in result.stdout

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["lab_id"] == "LAB-HW-10-PREREQ"
    assert payload["provider"] == "u-dma-buf"
    assert payload["size"] == 4 * 1024 * 1024
    assert payload["minimum_bytes"] == 2 * 1024 * 1024
    assert payload["sync_mode"] in (1, 2)
    assert payload["physical_base"] + payload["minimum_bytes"] <= 0x80000000


def test_lab10_udmabuf_preflight_source_rejects_unsafe_shortcuts():
    source = UDMABUF_PREFLIGHT.read_text(encoding="utf-8")
    assert "PREFLIGHT_REQUIRES_ROOT" in source
    assert "U_DMA_BUF_MODULE_NOT_LOADED" in source
    assert "DMA_BUFFER_OUTSIDE_HP0_DDR_LOW" in source
    assert "DMA_BUFFER_UNSAFE_SYNC_MODE" in source
    assert "TRANSPORT_PERMISSION_OR_POLICY" in source
    assert "ALLOWED_SYNC_MODES = {1, 2}" in source
    assert 'Path("/dev/udmabuf0")' in source
    assert 'Path("/dev/mem")' in source
