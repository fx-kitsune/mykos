#!/usr/bin/env python3
"""MyKOS M0 image tooling; uses only the Python standard library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "distribution/base/build.json"


def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def settings():
    return json.loads(CONFIG.read_text())


def packages():
    return [line.split("#", 1)[0].strip() for line in
            (ROOT / "distribution/packages/desktop.list.chroot").read_text().splitlines()
            if line.split("#", 1)[0].strip()]


def config_args(cfg):
    return ["--bootstrap", "debootstrap", "--mode", "ubuntu", "--distribution", cfg["suite"],
            "--architectures", cfg["architecture"], "--binary-images", "iso-hybrid",
            "--bootloader", cfg["bootloader"], "--syslinux-theme", "live-build", "--initramfs", "casper",
            "--linux-flavours", "generic", "--linux-packages", "linux-image",
            "--archive-areas", " ".join(cfg["archive_areas"]),
            "--mirror-bootstrap", cfg["mirror"], "--mirror-chroot", cfg["mirror"],
            "--mirror-binary", cfg["mirror"],
            "--mirror-chroot-security", cfg["security_mirror"],
            "--mirror-binary-security", cfg["security_mirror"],
            "--security", "true", "--volatile", "false",
            "--apt-secure", "true", "--apt-recommends", "true",
            "--debian-installer", "false", "--memtest", "none",
            "--iso-application", "MyKOS development live image",
            "--iso-volume", "MYKOS_0_1_DEV",
            "--bootappend-live", "boot=casper username=mykos hostname=mykos-live locales=en_US.UTF-8"]


def prepare_toolchain(destination):
    """Relocate the pinned Ubuntu toolchain, loading functions in the current shell."""
    prefix = Path(os.environ.get("MYKOS_LIVE_BUILD_PREFIX", "/usr"))
    shutil.copytree(prefix / "share/live/build", destination, symlinks=True)
    (destination / "scripts").mkdir(exist_ok=True)
    shutil.copy2(prefix / "lib/live/build.sh", destination / "scripts/build.sh")
    shutil.copytree(prefix / "lib/live/build", destination / "scripts/build")
    (destination / "bin").mkdir(exist_ok=True)
    shutil.copy2(prefix / "bin/lb", destination / "bin/lb")
    # Ubuntu's legacy scripts probe functions in a subshell. A relocated build
    # needs those functions sourced in the calling shell instead.
    old = '( . "${LIVE_BUILD}/scripts/build.sh" > /dev/null 2>&1 || true ) || . /usr/lib/live/build.sh'
    for script in [destination / "bin/lb", *(destination / "scripts/build").glob("*")]:
        if script.is_file():
            content = script.read_text()
            if old in content:
                script.write_text(content.replace(old, '. "${LIVE_BUILD}/scripts/build.sh"'))
    # Trên Noble, isohybrid nằm trong syslinux-utils, không phải syslinux.
    # Bước ISO chạy trong chroot nên cài công cụ trên host vẫn chưa đủ.
    iso_stage = destination / "scripts/build/lb_binary_iso"
    if iso_stage.is_file():
        content = iso_stage.read_text()
        iso_stage.write_text(content.replace(
            "Check_package chroot/usr/bin/isohybrid syslinux\n",
            "Check_package chroot/usr/bin/isohybrid syslinux-utils\n"))
    # Giai đoạn menu BIOS riêng tránh phụ thuộc Oneiric/gfxboot đã bị loại bỏ.
    shutil.copy2(ROOT / "distribution/image-build/lb_binary_syslinux",
                 destination / "scripts/build/lb_binary_syslinux")
    env = os.environ.copy()
    env["LIVE_BUILD"] = str(destination)
    env["PATH"] = str(destination / "bin") + ":" + env.get("PATH", "")
    return env


def configure(destination):
    # Never clean or reuse an existing build tree (may contain mounted filesystems).
    destination = destination.resolve()
    if destination.exists():
        raise ValueError(f"Build directory already exists: {destination}; choose a fresh path")
    destination.mkdir(parents=True)
    try:
        env = prepare_toolchain(destination / "toolchain")
        run(["lb", "config", *config_args(settings())], cwd=destination, env=env)
        config = destination / "config"
        (config / "package-lists").mkdir(exist_ok=True)
        shutil.copy2(ROOT / "distribution/packages/desktop.list.chroot", config / "package-lists")
        shutil.copytree(ROOT / "distribution/branding/overlay", config / "includes.chroot", dirs_exist_ok=True)
        installed = config / "includes.chroot"
        shutil.copytree(ROOT / "distribution/installer/overlay", installed, dirs_exist_ok=True)
        shutil.copytree(ROOT / "desktop/workspace", installed / "usr/share/mykos/workspace",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "requirements-dev.txt"))
        for relative, source in [("usr/bin/mykos-workspace", "mykos-workspace"),
                                 ("usr/share/applications/mykos-workspace.desktop", "mykos-workspace.desktop")]:
            target = installed / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "desktop/integration" / source, target)
        # Build hosts may use umask 077; installed assets must remain readable
        # and directories traversable by unprivileged desktop users.
        installed.chmod(0o755)
        for path in installed.rglob("*"):
            if not path.is_symlink():
                path.chmod(0o755 if path.is_dir() or path in {installed / "usr/bin/mykos-workspace", installed / "usr/bin/mykos-install"} else 0o644)
        hooks = config / "hooks"
        hooks.mkdir(exist_ok=True)
        shutil.copy2(ROOT / "distribution/image-build/010-mykos.chroot", hooks)
        archives = config / "archives"
        archives.mkdir(exist_ok=True)
        for suffix in ["chroot", "binary"]:
            shutil.copy2(ROOT / "distribution/repositories/mykos-updates.list",
                         archives / f"mykos-updates.list.{suffix}")
        shutil.copy2(CONFIG, destination / "mykos-build.json")
    except Exception:
        print(f"Configuration failed; retained diagnostics at {destination}", file=sys.stderr)
        raise
    return destination


def preflight():
    cfg = settings()
    problems = []
    if os.geteuid() != 0:
        problems.append("ISO creation requires root on a disposable build VM (chroot and mounts).")
    for tool in ["lb", "debootstrap", "mksquashfs", "xorriso", "genisoimage", "chroot", "mount", "isohybrid"]:
        if not shutil.which(tool):
            problems.append(f"Missing build tool: {tool}")
    if shutil.which("dpkg-query"):
        result = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "live-build"],
                                text=True, capture_output=True)
        if result.returncode or result.stdout.strip() != cfg["live_build_version"]:
            problems.append(f"Require Ubuntu live-build {cfg['live_build_version']} (not Debian live-build).")
    release = Path("/etc/os-release").read_text()
    if 'ID=ubuntu\n' not in release or 'VERSION_ID="24.04"' not in release:
        problems.append("Supported build host is Ubuntu 24.04 amd64.")
    if os.uname().machine != "x86_64":
        problems.append("Supported build host architecture is x86_64.")
    if shutil.disk_usage(ROOT).free < cfg["minimum_free_gib"] * 1024**3:
        problems.append(f"Require at least {cfg['minimum_free_gib']} GiB free at repository path.")
    return problems


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def metadata(image, destination, package_manifest):
    # Both files must come from the same successful build.
    if not image.is_file() or not package_manifest.is_file():
        raise ValueError("ISO and resolved package manifest must exist")
    if destination.exists():
        raise ValueError("Artifact directory already exists; refusing to overwrite")
    destination.mkdir(parents=True)
    cfg = settings()
    target = destination / f"mykos-{cfg['version']}-{cfg['architecture']}.iso"
    shutil.copy2(image, target)
    shutil.copy2(package_manifest, destination / "packages.txt")
    revision = run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True).stdout.strip()
    dirty = bool(run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True).stdout)
    inputs = {str(p.relative_to(ROOT)): sha256(p)
              for folder in ["distribution", "scripts/build", "desktop", "design-system/assets"]
              for p in sorted((ROOT / folder).rglob("*"))
              if p.is_file() and "__pycache__" not in p.parts}
    record = {"configuration": cfg, "git_revision": revision, "dirty": dirty,
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "input_sha256": inputs, "iso_sha256": sha256(target),
              "package_manifest_sha256": sha256(destination / "packages.txt"),
              "validation": "unvalidated; requires VM boot, install, desktop and hardware testing",
              "reproducibility": "rolling Ubuntu archive; not bit-for-bit reproducible"}
    (destination / "build.json").write_text(json.dumps(record, indent=2) + "\n")
    files = [target, destination / "packages.txt", destination / "build.json"]
    (destination / "SHA256SUMS").write_text("".join(f"{sha256(p)}  {p.name}\n" for p in files))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    configure_parser = sub.add_parser("configure")
    configure_parser.add_argument("directory", type=Path)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("directory", type=Path)
    build_parser.add_argument("--artifacts", type=Path, required=True)
    meta = sub.add_parser("metadata")
    meta.add_argument("image", type=Path)
    meta.add_argument("package_manifest", type=Path)
    meta.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        issues = preflight()
        print("\n".join(issues) if issues else "Build prerequisites passed")
        return int(bool(issues))
    if args.command == "configure":
        configure(args.directory)
    elif args.command == "build":
        issues = preflight()
        if issues:
            raise ValueError("\n".join(issues))
        if args.artifacts.exists():
            raise ValueError("Artifact directory already exists")
        directory = configure(args.directory)
        # Keep the complete log even when live-build fails.
        print(f"Nhật ký tạo ảnh: {directory / 'build.log'}", flush=True)
        with (directory / "build.log").open("w") as log:
            env = os.environ.copy()
            env["LIVE_BUILD"] = str(directory / "toolchain")
            env["PATH"] = str(directory / "toolchain/bin") + ":" + env.get("PATH", "")
            run(["lb", "build"], cwd=directory, env=env, stdout=log, stderr=subprocess.STDOUT)
        images = list(directory.glob("*.iso"))
        if len(images) != 1:
            raise ValueError("Expected exactly one ISO in completed build")
        metadata(images[0], args.artifacts, directory / "chroot.packages.live")
        shutil.copy2(directory / "build.log", args.artifacts)
        for name in ["bootstrap", "chroot", "binary", "common"]:
            shutil.copy2(directory / "config" / name, args.artifacts / f"live-build-{name}.conf")
        (args.artifacts / "SHA256SUMS").write_text("".join(
            f"{sha256(p)}  {p.name}\n" for p in sorted(args.artifacts.iterdir())
            if p.is_file() and p.name != "SHA256SUMS"))
    elif args.command == "metadata":
        metadata(args.image, args.destination, args.package_manifest)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"mykos: {error}", file=sys.stderr)
        sys.exit(1)
