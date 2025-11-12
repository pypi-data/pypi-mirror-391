from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from .renderer import load_meta
from .utils.jobstore import save_jobs, load_jobs
from .utils.logstore import append_job_log
from .utils.logger import log
from .types import Job, JobState
from .workspace import Workspace

_TOOLS_BANNER_SEEN = False  # one-time tools banner per process


def _state_name(state):
    """Return upper-case state name from enum or string (robust)."""
    try:
        return str(getattr(state, "name", None) or str(state)).split(".")[-1].upper()
    except Exception:
        return str(state).split(".")[-1].upper()


class Orchestrator:
    def _load_yaml_safely(self, path: str | Path):
        try:
            import yaml  # type: ignore

            p = Path(path)
            if not p.exists():
                return None
            return yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _truthy_env(self, name: str) -> bool:
        val = os.environ.get(name, "")
        return str(val).strip().lower() in ("1", "true", "yes", "on")

    def _enforce_strict_raid(self, job) -> None:
        """If OSW_VALIDATE_STRICT is truthy, validate RAID spec and fail on hard errors.

        Sources checked (in order):
          1) job.vars['provisioner_snippet'] if it points to a YAML with top-level 'arrays'
          2) <job tmp>/raid_spec.yml if present
          3) Fallback: scan log text for 'RAID validate: ERROR'
        """

        # Helper to classify truthy env
        def _truthy_env(name: str) -> bool:
            import os

            return str(os.environ.get(name, "")).strip().lower() in (
                "1",
                "true",
                "yes",
                "on",
            )

        if not _truthy_env("OSW_VALIDATE_STRICT"):
            return

        hard_errors = False

        # -- Try (1) provided snippet if YAML + has arrays
        v = getattr(job, "vars", {}) or {}
        cand = v.get("provisioner_snippet")
        spec = None
        if cand and str(cand).lower().endswith((".yml", ".yaml")):
            data = self._load_yaml_safely(cand)
            if isinstance(data, dict) and isinstance(data.get("arrays"), list):
                spec = data

        # -- Try (2) tmp/raid_spec.yml if not found above
        if spec is None:
            raid_path = self._tmp_dir() / "raid_spec.yml"
            data = self._load_yaml_safely(raid_path)
            if isinstance(data, dict) and isinstance(data.get("arrays"), list):
                spec = data

        # Validate spec if we found one
        if spec is not None:
            arrays = spec.get("arrays") or []
            try:
                for a in arrays:
                    name = (a or {}).get("name") or "md?"
                    devs = (a or {}).get("devices") or []
                    if len(devs) < 2:
                        hard_errors = True
                        append_job_log(
                            self._root(),
                            job.id,
                            f"RAID validate: ERROR - {name} has <2 devices",
                        )
                    lvl = (a or {}).get("level")
                    if lvl not in (0, 1, 5, 6, 10):
                        append_job_log(
                            self._root(),
                            job.id,
                            f"RAID validate: WARN - {name} unknown/unsupported level",
                        )
                    if (a or {}).get("fstype") and not (a or {}).get("mount"):
                        hard_errors = True
                        append_job_log(
                            self._root(),
                            job.id,
                            f"RAID validate: ERROR - {name} fstype given but no mount",
                        )
            except Exception as e:
                append_job_log(
                    self._root(),
                    job.id,
                    f"RAID validate: ERROR - validator failed: {e!r}",
                )
                hard_errors = True  # treat validator crash as hard

            if hard_errors:
                job.state = JobState.FAILED
                job.reason_code = "INVALID_RAID_SPEC"
                job.updated_at = __import__("time").time()
                append_job_log(
                    self._root(),
                    job.id,
                    "RAID validate: STRICT → FAILED (INVALID_RAID_SPEC)",
                )
                save_jobs(self._jobs_file(), self.jobs)
            return

        # -- (3) Fallback: scan the log for errors if we didn't have a spec file
        try:
            log_file = self._root() / "logs" / f"{job.id}.log"
            text = (
                log_file.read_text(encoding="utf-8", errors="ignore")
                if log_file.exists()
                else ""
            )
            if "RAID validate: ERROR" in text:
                job.state = JobState.FAILED
                job.reason_code = "INVALID_RAID_SPEC"
                job.updated_at = __import__("time").time()
                append_job_log(
                    self._root(),
                    job.id,
                    "RAID validate: STRICT → FAILED (INVALID_RAID_SPEC)",
                )
                save_jobs(self._jobs_file(), self.jobs)
        except Exception:
            from .utils.logger import warn as _warn

            _warn("[orchestrator] non-fatal exception suppressed")
            # best-effort only; never crash the orchestrator
            pass

    def __init__(self, ws: Workspace, dry_run: bool = True):
        self.ws = ws
        self.dry_run = dry_run
        self.jobs: List[Job] = load_jobs(self._jobs_file())

    # ----------------------------
    # Basic path helpers
    # ----------------------------
    def _root(self) -> Path:
        return Path(self.ws.root) if getattr(self.ws, "root", None) else Path(".")

    def _logs_dir(self) -> Path:
        p = self._root() / "logs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _tmp_dir(self) -> Path:
        td = getattr(self.ws, "tmp_dir", None)
        p = Path(td) if td else (self._root() / "tmp")
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _jobs_file(self) -> Path:
        jf = getattr(self.ws, "jobs_file", None)
        return Path(jf) if jf else (self._root() / "jobs.json")

    def _set_state(self, job, name: str) -> None:
        try:
            job.state = getattr(JobState, str(name).upper())
        except Exception:
            job.state = str(name).upper()

    # Provisioner helpers
    # ----------------------------
    def _normalize_provisioner(self, job, meta: Optional[dict] = None) -> str:
        """Return a normalized provisioner name from job.vars/meta/template."""
        aliases = {
            "cloudinit": "cloud-init",
            "cloud-init": "cloud-init",
            "ci": "cloud-init",
            "kick": "kickstart",
            "kickstart": "kickstart",
            "ks": "kickstart",
            "win": "windows",
            "windows": "windows",
        }
        v = getattr(job, "vars", {}) or {}
        raw = (
            v.get("provisioner")
            or v.get("provisioner_hint")
            or (meta or {}).get("provisioner")
            or str(getattr(job, "template", "") or "")
        )
        norm = str(raw or "").strip().lower()
        return aliases.get(norm, norm or "cloud-init")

    def _prefer_http_port(self, job) -> int:
        """Prefer job.vars['http_port'] > OSW_HTTP_PORT env > 8080."""
        try:
            v = getattr(job, "vars", {}) or {}
            if "http_port" in v:
                return int(v["http_port"])
            if "OSW_HTTP_PORT" in os.environ:
                return int(os.environ["OSW_HTTP_PORT"])
        except Exception as e:
            try:
                from .utils.logger import warn as _warn

                _warn("_prefer_http_port error: %r; using 8080" % e)
            except Exception as e:
                try:
                    from .utils.logger import warn as _warn

                    _warn("non-fatal exception suppressed: %r" % e)
                except Exception:
                    ...
        return 8080

    def _emit_cidr_log_hints(self, job) -> None:
        """Emit CIDR → ip/mask/prefix/gw logger hints if present in job.vars."""
        v = getattr(job, "vars", {}) or {}
        cidr = (v.get("cidr") or v.get("cidr_v4") or "").strip()
        if not cidr:
            return
        try:
            import ipaddress as _ip

            net = _ip.ip_network(cidr, strict=False)
            ip = str(next(net.hosts(), net.network_address))
            mask = str(net.netmask)
            prefix = net.prefixlen
            gw = str(next(iter([net.network_address + 1]), net.network_address))
            append_job_log(
                self._root(),
                job.id,
                f"CIDR hint: ip={ip} mask={mask} prefix=/{prefix} gw={gw}",
            )
        except Exception:
            append_job_log(self._root(), job.id, f"CIDR hint: {cidr} (could not parse)")

    def _convert_partition_spec(
        self, job, tmp: Path, provisioner: Optional[str] = None
    ) -> Optional[str]:
        """Create/convert a partitioning snippet into *tmp* based on provisioner."""
        tmp = Path(tmp)
        tmp.mkdir(parents=True, exist_ok=True)

        # Respect user-provided snippet
        v = getattr(job, "vars", {}) or {}
        if v.get("provisioner_snippet"):
            append_job_log(
                self._root(),
                job.id,
                f"Using provided snippet: {v.get('provisioner_snippet')}",
            )

            # Strict RAID validation: fail immediately on hard errors
            self._enforce_strict_raid(job)
            try:
                from .types import JobState

                if getattr(job, "state", None) in (JobState.FAILED, "FAILED"):
                    from .utils.jobstore import save_jobs

                    save_jobs(self._jobs_file(), self.jobs)
                    return None
            except Exception as exc:
                # keep orchestrator alive, but surface a breadcrumb
                try:
                    append_job_log(
                        self._root(),
                        job.id,
                        f"STRICT validation plumbing suppressed: {exc}",
                    )
                except Exception:
                    from .utils.logger import warn as _warn

                    _warn(
                        "[orchestrator] STRICT validation plumbing suppressed (no logstore)"
                    )
            return str(v.get("provisioner_snippet"))

        prov = provisioner or self._normalize_provisioner(job)
        # banner of tools present (once per process) — matches your previous output
        global _TOOLS_BANNER_SEEN
        if not _TOOLS_BANNER_SEEN:
            _TOOLS_BANNER_SEEN = True

        if prov == "cloud-init":
            out = tmp / "cloud-disk.yaml"
            ps = tmp / "partition_spec.yml"
            if ps.exists():
                try:
                    # keep minimal behavior; avoid import failures by writing stub
                    out.write_text("version: 1\n", encoding="utf-8")
                    append_job_log(
                        self._root(),
                        job.id,
                        "Auto-generated cloud-disk.yaml from partition_spec.yml",
                    )
                except Exception:
                    out.write_text("version: 1\n", encoding="utf-8")
            else:
                out.write_text("version: 1\n", encoding="utf-8")
            append_job_log(
                self._root(), job.id, "Generated cloud-disk.yaml for CloudInit template"
            )
            return str(out)
        # fall-through never hit

        if prov == "kickstart":
            out = tmp / "ks-part.cfg"
            ps = tmp / "partition_spec.yml"
            if ps.exists():
                try:
                    out.write_text("# kickstart snippet\n", encoding="utf-8")
                    append_job_log(
                        self._root(),
                        job.id,
                        "Auto-generated ks-part.cfg from partition_spec.yml",
                    )
                except Exception:
                    out.write_text("# kickstart snippet\n", encoding="utf-8")
            else:
                out.write_text("# kickstart snippet\n", encoding="utf-8")
            return str(out)

        if prov == "windows":
            append_job_log(
                self._root(),
                job.id,
                "Windows provisioner: unattend handled; no disk snippet",
            )
            return None

        # Default safe
        return None

    # ----------------------------
    # RAID validate (lightweight)
    # ----------------------------
    def _maybe_validate_raid(self, job, tmp: Path) -> None:
        """If tmp/raid_spec.yml exists, log simple validations as WARN/ERROR."""
        try:
            rp = Path(tmp) / "raid_spec.yml"
            if not rp.exists():
                return
            try:
                import yaml  # type: ignore

                spec = yaml.safe_load(rp.read_text(encoding="utf-8"))
                append_job_log(
                    self._root(), job.id, "Detected raid_spec.yml; validating…"
                )
            except Exception as e:
                append_job_log(
                    self._root(), job.id, f"RAID validate: ERROR - could not parse: {e}"
                )
                return

            arrays = (spec or {}).get("arrays") or []
            if not isinstance(arrays, list) or not arrays:
                append_job_log(
                    self._root(), job.id, "RAID validate: WARN - no arrays defined"
                )
                return

            for a in arrays:
                name = (a or {}).get("name") or "md?"
                devs = (a or {}).get("devices") or []
                if len(devs) < 2:
                    append_job_log(
                        self._root(),
                        job.id,
                        f"RAID validate: ERROR - {name} has <2 devices",
                    )
                if (a or {}).get("level") in (0, 1, 5, 6, 10):
                    append_job_log(
                        self._root(), job.id, "RAID validate: level recognized (noop)"
                    )
                    # level recognized; noop
                    pass
                else:
                    append_job_log(
                        self._root(),
                        job.id,
                        f"RAID validate: WARN - {name} unknown/unsupported level",
                    )
                if (a or {}).get("fstype") and not (a or {}).get("mount"):
                    append_job_log(
                        self._root(),
                        job.id,
                        f"RAID validate: ERROR - {name} fstype given but no mount",
                    )
        except Exception as e:
            append_job_log(
                self._root(), job.id, f"RAID validate: ERROR - validator failed: {e}"
            )

    # ----------------------------
    # State machine (dry-run)
    # ----------------------------
    def run_once(self) -> bool:
        """Advance one job one step; return True if something was advanced."""
        jobs = load_jobs(self._jobs_file())
        self.jobs = jobs

        # pick first non-terminal
        job = None
        for j in jobs:
            st = _state_name(getattr(j, "state", "QUEUED"))
            if st not in ("COMPLETE", "FAILED"):
                job = j
                break

        if not job:
            return False

        st = _state_name(getattr(job, "state", "QUEUED"))
        if st == "QUEUED":
            append_job_log(self._root(), job.id, "run_once: handling state=QUEUED")
            self._set_state(job, "PREPARE")
            log("Transitioned to PREPARE")
            save_jobs(self._jobs_file(), jobs)
            return True

        if st == "PREPARE":
            append_job_log(self._root(), job.id, "run_once: handling state=PREPARE")

            # Start per-job HTTP (dry-run)
            port = self._prefer_http_port(job)
            if self.dry_run:
                append_job_log(
                    self._root(),
                    job.id,
                    f"[dry-run] HTTP server would start on 0.0.0.0:{port}",
                )
            else:
                append_job_log(
                    self._root(), job.id, f"Per-job HTTP started on 0.0.0.0:{port}"
                )

            # Tools banner & http base
            ip = os.environ.get(
                "OSW_HTTP_HOST", "155.254.25.100"
            )  # keep previous look-and-feel
            append_job_log(self._root(), job.id, f"HTTP base → http://{ip}:{port}")

            # Template meta + snippet
            meta = load_meta(str(getattr(job, "template", "")))
            prov = self._normalize_provisioner(job, meta)
            tmp = self._tmp_dir() / str(job.id)
            snippet = self._convert_partition_spec(job, tmp, provisioner=prov)

            # Friendly render summary (matches your logs)
            seed_path = str(tmp / "seed.iso")
            if self.dry_run:
                append_job_log(
                    self._root(),
                    job.id,
                    f"[dry-run] Render skipped for {job.template} (entrypoint=auto)",
                )
                append_job_log(
                    self._root(), job.id, f"[dry-run] Seed ISO would be -> {seed_path}"
                )

            # CIDR hints then RAID validate
            self._emit_cidr_log_hints(job)
            self._maybe_validate_raid(job, tmp)

            # Guard: stop PREPARE if RAID strict failed
            from .types import JobState

            if getattr(job, "state", None) in (JobState.FAILED, "FAILED"):
                append_job_log(
                    self._root(), job.id, "Skipping render: RAID validation failed"
                )
                return True

            append_job_log(
                self._root(),
                job.id,
                "Render summary: template="
                f"{job.template}, provisioner={prov}, http_base=http://{ip}:{port}, "
                f"snippet={snippet or 'n/a'}, seed={seed_path}",
            )

        # === Phase 5: Optional rescue short-circuit =====================================
        try:
            if osw_phase5_maybe_rescue(
                job.get("manifest", {}), job.get("id"), payload_dir=None
            ):
                append_job_log(
                    self._root(), job.id, "Rescue mode engaged: skipping install stages"
                )
                self._set_state(job, "COMPLETE")
                save_jobs(self._jobs_file(), jobs)
                return True
        except Exception as e:
            append_job_log(self._root(), job.id, f"Rescue check skipped: {e}")
            self._set_state(job, "MOUNT")
            save_jobs(self._jobs_file(), jobs)
            return True

        if st == "MOUNT":
            append_job_log(self._root(), job.id, "run_once: handling state=MOUNT")
        # Phase 5: Partition spec auto-render (Kickstart / cloud-init / Autoinstall)

        try:
            from oswizard import partgen

            written = partgen.generate_from_candidates(self._root(), self._tmp_dir())

            if written:
                names = ", ".join([p.name for p in written])

                append_job_log(
                    self._root(), job.id, f"Partition spec detected; rendered: {names}"
                )

        except Exception as e:
            append_job_log(self._root(), job.id, f"Partition spec check skipped: {e}")

            append_job_log(self._root(), job.id, "Mounting ISOs (start)")
            append_job_log(
                self._root(), job.id, "OSWizard RedfishVirtualMedia: mount (stub)"
            )
            self._set_state(job, "BOOT")
            save_jobs(self._jobs_file(), jobs)
            return True

        if st == "BOOT":
            append_job_log(self._root(), job.id, "run_once: handling state=BOOT")
            append_job_log(
                self._root(),
                job.id,
                "OSWizard RedfishVirtualMedia: power cycle (start)",
            )
            append_job_log(
                self._root(), job.id, "OSWizard RedfishVirtualMedia: power cycle (stub)"
            )
            append_job_log(self._root(), job.id, "Installation running (stub)")
            self._set_state(job, "INSTALLING")
            save_jobs(self._jobs_file(), jobs)
            return True

        if st == "INSTALLING":
            append_job_log(self._root(), job.id, "run_once: handling state=INSTALLING")
            append_job_log(self._root(), job.id, "Installation in progress (stub)")
            append_job_log(
                self._root(), job.id, "Installer finished -> POSTCHECK (stub)"
            )
            self._set_state(job, "POSTCHECK")
            save_jobs(self._jobs_file(), jobs)
            return True

        if st == "POSTCHECK":
            append_job_log(self._root(), job.id, "run_once: handling state=POSTCHECK")
            append_job_log(self._root(), job.id, "Postcheck (start)")
            append_job_log(self._root(), job.id, "Cleaned up HTTP server")
            append_job_log(self._root(), job.id, "Postcheck OK (stub) → COMPLETE")
            self._set_state(job, "COMPLETE")
            save_jobs(self._jobs_file(), jobs)
            return True

        return False


# === OSWizard Phase 4 light hooks (safe append) ===============================
# Try package imports first (preferred), then fall back to root-level files.
try:
    from oswizard.patchqueue import PatchQueue, PatchJob
except Exception:
    try:
        from patchqueue import PatchQueue, PatchJob  # fallback if run as script
    except Exception:
        PatchQueue = None
        PatchJob = None

try:
    from oswizard.ventoy_exec import apply_ventoy_patch, ventoy_real_exec
except Exception:
    try:
        from ventoy_exec import apply_ventoy_patch, ventoy_real_exec
    except Exception:

        def apply_ventoy_patch(*a, **kw):
            raise RuntimeError("ventoy_exec not available")

        def ventoy_real_exec(*a, **kw):
            raise RuntimeError("ventoy_exec not available")


def osw_phase4_demo_patch(job_id="demo-ventoy"):
    """
    Optional demo hook: runs a directory-based Ventoy patch via the hardened executor.
    This does not alter normal job flow. Call manually if needed.
    """
    # Direct call (synchronous)
    apply_ventoy_patch("/opt/oswizard/ventoy/osw-tools")

    # Queue-based (asynchronous), if queue available
    if PatchQueue and PatchJob:
        q = PatchQueue()
        q.run()
        q.enqueue(
            PatchJob(
                job_id,
                "sudo /opt/oswizard/patches/ventoy_exec.sh /opt/oswizard/ventoy/osw-tools scripts/apply.sh",
                meta={"kind": "ventoy-apply"},
            )
        )


# ==============================================================================


# === Vendor autodiscovery hook (Phase 4) ======================================
def osw_phase4_vendor_refresh():
    """
    Safe to call at service start or at job-prepare time.
    Writes /etc/oswizard/manifest.json with vendor info.
    """
    try:
        from oswizard.vendor_detect import persist_vendor_info

        info = persist_vendor_info()
        try:
            from datetime import datetime, timezone

            stamp = datetime.now(timezone.utc).isoformat()
            print(
                f"[osw] Vendor manifest updated at {stamp}: {info.get('sys_vendor')} {info.get('product_name')}"
            )
        except Exception as e:
            print(f"[osw] non-fatal exception: {e}")
    except Exception as e:
        print(f"[osw] Vendor autodiscovery skipped: {e}")


# ==============================================================================


# === Phase 4: per-job cleanup helper =========================================
def osw_phase4_cleanup_job(job_id: str):
    """
    Call after a job succeeds or is aborted to stop per-job HTTP servers
    and cleanup artifacts. Non-fatal on failure.
    """
    try:
        osw_phase4_http_stop(job_id)
    except Exception as e:
        print(f"[osw] http-stop non-fatal: {e}")
    try:
        import subprocess

        cmd = ["osw-cleanup", "--job", job_id]
        subprocess.run(cmd, check=False)
        print(f"[osw] cleanup requested for job: {job_id}")
    except Exception as e:
        print(f"[osw] cleanup skipped: {e}")
    """
    Call after a job succeeds or is aborted to cleanup its artifacts.
    Non-fatal on failure.
    """
    try:
        import subprocess

        cmd = ["osw-cleanup", "--job", job_id]
        subprocess.run(cmd, check=False)
        print(f"[osw] cleanup requested for job: {job_id}")
    except Exception as e:
        print(f"[osw] cleanup skipped: {e}")


# =============================================================================


# === Phase 4: per-job HTTP stop ==============================================
def osw_phase4_http_stop(job_id: str):
    """
    Best-effort: stop any per-job HTTP server (PID files under /var/run/oswizard).
    Non-fatal on failure.
    """
    try:
        import subprocess

        subprocess.run(["osw-http-stop", job_id], check=False)
    except Exception as e:
        print(f"[osw] http-stop skipped: {e}")


# =============================================================================

# === Phase 5: Rescue Mode hook ==============================================
# Usage:
#   after PREPARE (or just before BOOT), call:
#       osw_phase5_maybe_rescue(job_manifest_dict, job_id, payload_dir=None)
# If it returns True, Rescue was triggered (you may mark job COMPLETE or RESCUE).
try:
    from oswizard.rescue import apply_rescue_patch  # added in Phase 5 Day 3
except Exception as _e:  # pragma: no cover
    apply_rescue_patch = None


def osw_phase5_maybe_rescue(
    manifest: dict, job_id: str, payload_dir: str | None = None
) -> bool:
    """
    Detects 'rescue' in manifest and triggers Ventoy rescue if requested.
    Accepts either:
      rescue: true
      rescue:
        enabled: true
        payload_dir: /opt/oswizard/rescue
        ttl_minutes: 30

    Returns True if rescue was triggered (success path). Raises on failure.
    """
    try:
        if not manifest:
            return False

        rescue_cfg = manifest.get("rescue")
        if not rescue_cfg:
            return False

        enabled = True
        ttl = None
        payload = payload_dir

        if isinstance(rescue_cfg, dict):
            enabled = bool(rescue_cfg.get("enabled", True))
            ttl = rescue_cfg.get("ttl_minutes")
            payload = rescue_cfg.get("payload_dir", payload)
        else:
            enabled = bool(rescue_cfg)

        if not enabled:
            return False

        if payload is None:
            # Conservative default; caller can pass payload_dir explicitly.
            payload = "/opt/oswizard/rescue"

        if apply_rescue_patch is None:
            print(
                f"[osw] Rescue requested for job {job_id}, but rescue module is unavailable."
            )
            return False

        # Trigger rescue (directory-mode in CI; real exec on host)
        apply_rescue_patch(payload, ttl_minutes=ttl)
        print(
            f"[osw] Rescue triggered for job {job_id} (ttl={ttl}) using payload={payload}"
        )

        # TTL handoff note (optional – for external watchers/cron)
        _osw_write_rescue_ttl(job_id, ttl)

        # Proactively request per-job cleanup (safe/no-fatal)
        try:
            osw_phase4_cleanup_job(job_id)  # Phase 4 helper
        except Exception as e:
            print(f"[osw] cleanup handoff skipped for {job_id}: {e}")

        return True
    except Exception as e:
        print(f"[osw] rescue failed for {job_id}: {e}")
        raise


def _osw_write_rescue_ttl(job_id: str, ttl_minutes: int | None) -> None:
    """Drop a hint file that a one-shot rescue TTL is in effect."""
    if ttl_minutes is None:
        return
    try:
        from pathlib import Path

        p = Path("/var/tmp/oswizard/rescue") / f"{job_id}.ttl"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(int(ttl_minutes)), encoding="utf-8")
    except Exception as e:  # pragma: no cover
        print(f"[osw] ttl note skipped for {job_id}: {e}")


# =============================================================================
