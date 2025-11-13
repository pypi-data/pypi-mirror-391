from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path
from .utils.logger import log


def _which_any(*names: str) -> str | None:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def build_combined_iso(
    os_iso_path: str, seed_dir: str, out_iso_path: str, boot_args: str
) -> bool:
    """
    Remaster an ISO that embeds seed files and appends boot args.
    Minimal, best-effort:
      - mounts/unsquashes ISO contents to a temp dir
      - copies seed files into root (e.g., ks.cfg or preseed.cfg already there from renderer)
      - tries to patch grub/syslinux to add boot_args
      - writes a new ISO via xorriso/genisoimage/mkisofs
    Returns True on success, False otherwise.
    """
    tool = _which_any("xorriso", "genisoimage", "mkisofs")
    if not tool:
        log(
            "[warn] No ISO tool available (xorriso/genisoimage/mkisofs); skipping combined ISO build"
        )
        return False

    os_iso = Path(os_iso_path)
    seed_dir = Path(seed_dir)
    out_iso = Path(out_iso_path)
    if not os_iso.exists():
        log(f"[warn] OS ISO not found at {os_iso}; cannot combine")
        return False

    tmp = Path(tempfile.mkdtemp(prefix="osw-combine-"))
    work = tmp / "iso"
    work.mkdir(parents=True, exist_ok=True)

    # 1) Attempt to extract ISO (best effort). We avoid root deps; use xorriso -osirrox if available.
    extracted = False
    try:
        if tool.endswith("xorriso"):
            # extract whole tree
            cmd = [
                tool,
                "-osirrox",
                "on",
                "-indev",
                str(os_iso),
                "-extract",
                "/",
                str(work),
            ]
            subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            extracted = True
    except Exception:
        import logging

        logging.getLogger(__name__).debug(
            "suppressed exception in try/except", exc_info=True
        )
    if not extracted:
        log(
            "[warn] Could not extract ISO contents; combined ISO may not include boot arg patch"
        )
        return False

    # 2) Copy seed files into ISO root (renderer should have created them in seed_dir)
    for p in seed_dir.glob("*"):
        if p.is_file():
            shutil.copy2(p, work / p.name)

    # 3) Try to patch common boot configs (grub/syslinux/isolinux)
    def _try_patch(path: Path) -> bool:
        try:
            text = path.read_text(errors="ignore")
            # naive append of boot args to linux/linuxefi lines
            text2 = text.replace(" linux ", f" linux {boot_args} ")
            text2 = text2.replace(" linuxefi ", f" linuxefi {boot_args} ")
            text2 = text2.replace(" append ", f" append {boot_args} ")
            if text2 != text:
                path.write_text(text2)
                return True
        except Exception:
            import logging

            logging.getLogger(__name__).debug(
                "suppressed exception in try/except", exc_info=True
            )
        return False

    patched = False
    candidates = [
        work / "boot/grub/grub.cfg",
        work / "EFI/BOOT/grub.cfg",
        work / "isolinux/isolinux.cfg",
        work / "syslinux/syslinux.cfg",
        work / "boot/grub2/grub.cfg",
    ]
    for c in candidates:
        if c.exists():
            if _try_patch(c):
                patched = True

    if not patched:
        log(
            "[warn] Could not patch boot configs; combined ISO will include seed but boot menu might still need manual edit"
        )

    # 4) Rebuild ISO
    try:
        if tool.endswith("xorriso"):
            # minimal flags; you can add -isohybrid-mbr etc if you need hybrid
            cmd = [
                tool,
                "-as",
                "mkisofs",
                "-J",
                "-R",
                "-V",
                "OSW-COMBINED",
                "-o",
                str(out_iso),
                str(work),
            ]
        else:
            cmd = [
                tool,
                "-J",
                "-R",
                "-V",
                "OSW-COMBINED",
                "-o",
                str(out_iso),
                str(work),
            ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log(f"[ok] Built combined ISO → {out_iso}")
        return True
    except Exception as e:
        log(f"[err] Combined ISO build failed: {e}")
        return False
