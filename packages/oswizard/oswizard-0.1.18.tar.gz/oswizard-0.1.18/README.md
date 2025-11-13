# OSWizard CLI (Prototype)

[![Release](badges/release.svg)](https://github.com/oswiz-alt/oswizard-cli/tags)

[![Lint](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/lint.yml)
[![CI](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)  ![Ruff](https://img.shields.io/badge/lint-ruff-informational)

[![CI](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)  ![Ruff](https://img.shields.io/badge/lint-ruff-informational)

## Quickstart

```bash
# install deps
poetry install     # or: pip install -e .

# init workspace
poetry run osw init ./osw-work

# add a machine (fake for now)
poetry run osw machines add --name lab-01 --host 10.0.0.50 --user ADMIN --password PASS

# submit a job
poetry run osw jobs submit --machine lab-01 --template ubuntu-24.04 \\
  --var hostname=lab-01 --var ssh_key="$(cat ~/.ssh/id_rsa.pub 2>/dev/null || echo test-key)"

# run it once (advances states; IPMI is stubbed)
poetry run osw jobs run --id <job-id-from-list>

# watch logs (static snapshot for now)
poetry run osw jobs watch --id <job-id-from-list>
```

## Notes
- This prototype does not touch real hardware yet; IPMI commands are stubbed.
- Next steps: add worker loop, retries, real `ipmitool`, switch Ubuntu to Autoinstall.

## 🚀 OSWizard Product Roadmap (2025 Q1–Q3)

| Quarter | Focus Area | Key Milestones |
|----------|-------------|----------------|
| **Q1 2025** | 🧩 **Core Stability & Validation** | - Full RAID & partition schema validation  <br> - Redfish & IPMI integration (Dell, HP, Lenovo, **Supermicro**) <br> - Secure local workspace persistence |
| **Q2 2025** | ⚙️ **Portal & User Experience** | - Web dashboard (React-based) for deployments <br> - IPMI **console view (no Java)**  <br> - Networking setup during install (custom IP & subnet) <br> - Enhanced logging & diagnostics API |
| **Q3 2025** | ☁️ **Enterprise & Premium+ Expansion** | - Power control actions (Power On/Off, Reset, Reboot) from portal <br> - Multi-node batch provisioning <br> - Tenant-ready templates for hosting providers <br> - CI/CD-backed test suite & deployment automation |
| **Beyond Q3** | 🌐 **AI & Smart Automation** | - Predictive install validation (AI-aided) <br> - Hardware failure predictions <br> - Workflow orchestration between data centers |

---

###

### 🚀 OSWizard Product Roadmap (Nov 2025 → Feb 2026)

Quarter / Phase | Focus Area | Key Milestones
---|---|---
**Nov–Dec 2025** | 🧩 Core Finish & Integrations | Custom partition profiles (LVM/RAID) schema + renderers · Ventoy **Rescue Mode** (iDRAC first) · VirtualMedia slot probing (real impl) · API v1 scaffold (Jobs submit/status)
**Jan 2026** | ⚙️ WHMCS + API + Portal Alpha | WHMCS module (Reinstall/Rescue/Power) via REST · API v1 power/rescue endpoints · Portal Alpha: FastAPI backend + Next.js UI (live job logs)
**Feb 2026** | 🚀 Launch Readiness | Docs site (MkDocs) + ARCHITECTURE/DEVELOPER guides · CI release pipeline (tagged builds / optional PyPI) · GA hardening & partner onboarding

🧱 Technical Highlights (Merged & Updated)

- ✅ IPMI / Redfish / Supermicro **with vendor autodetect**
- 🌐 Custom IP assignment during installation
- 🧩 **Custom partition profiles** (plain/LVM/RAID) → Kickstart / Autoinstall / cloud-init renderers
- 🛟 Ventoy-based **Rescue Mode** (one-shot boot with TTL)
- 🔌 **WHMCS module + REST API v1** (jobs, power, rescue)
- 🖥️ HTML5 console (SOL / noVNC) **+ power control** — no Java
- 🔒 Secure local workspace with **per-job cleanup + retention**
- 🧪 CI matrix (Ubuntu + Alma) + lint/format/test badges (GitHub Actions)
- 🧰 Local HTTP per-job server with auto-cleanup
- 🧩 Designed for Hosting Providers, MSPs, and Enterprises

- ✅ IPMI / Redfish / Supermicro support  
- 🌐 Custom IP assignment during installation  
- 🖥️ Browser-based console view (no Java)  
- ⚡ Power control (Premium+): on/off/reset/reboot  
- 🔒 Secure local workspace with per-job cleanup  
- 🧰 CI-ready with lint/test badges and GitHub Actions  
- 🧩 Designed for Hosting Providers, MSPs, and Enterprises  

---

> **Launch Target:** 2025 Q3  
> **Goal:** Simplify bare-metal OS deployment — _no Java, no pain, full automation._

## OSWizard Phase 3–4 Notes
- **WireGuard:** see `docs/wireguard-topology.md` for peer config, firewall, and verification steps.
- **Ventoy Real Exec:** hardened executor at `/opt/oswizard/patches/ventoy_exec.sh` with Python wrapper `oswizard/ventoy_exec.py`.
- **Vendor Autodiscovery:** run `osw_phase4_vendor_refresh()` to write `/etc/oswizard/manifest.json`.
- **Session Cleanup:** `osw-cleanup --sweep` or `--job <id>`, timer `oswizard-cleanup.timer`, config `/etc/oswizard/cleanup.json`.


---

## CI Status & Summary

[![Lint](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/lint.yml/badge.svg)](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/lint.yml)
[![Tests](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/tests.yml)

### Phase 4 Highlights
- ✅ **Ventoy Executor** – real exec wrapper & patch scripts  
- ✅ **Vendor Autodiscovery** – manifest writer & logs  
- ✅ **Session Cleanup Daemon** – sweep + per-job timer  
- ✅ **HTTP Auto-Stop** – per-job HTTP shutdown before cleanup  
- ✅ **CI & Tests** – lint + pytest pipeline (green)

---


[![Integration Tests (Ventoy)](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/integration.yml/badge.svg)](https://github.com/oswiz-alt/oswizard-cli/actions/workflows/integration.yml)

- Ventoy **Rescue Mode** directory & host-script wrappers (Step 1)

### 🔧 Rescue Mode (directory payload)
Add to your job manifest:
```yaml
rescue:
  enabled: true
  payload_dir: /opt/oswizard/rescue
  ttl_minutes: 30

Quick local smoke (directory-mode stub):

mkdir -p /opt/oswizard/rescue/scripts
printf '#!/usr/bin/env bash\necho RESCUE_OK\n' >/opt/oswizard/rescue/scripts/rescue.sh
chmod +x /opt/oswizard/rescue/scripts/rescue.sh
python -c "import oswizard.rescue as r; r.apply_rescue_patch('/opt/oswizard/rescue', ttl_minutes=5)"

