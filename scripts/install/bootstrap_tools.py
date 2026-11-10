"""Prepare verified Debian bootstrap tools without trusting an old rescue keyring."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

HERE = Path(__file__).resolve().parent
HOST_PACKAGES = {'findmnt':'util-linux', 'lsblk':'util-linux', 'mount':'util-linux',
                 'umount':'util-linux', 'swapoff':'util-linux', 'sfdisk':'fdisk',
                 'mkfs.fat':'dosfstools', 'mkfs.ext4':'e2fsprogs', 'udevadm':'udev',
                 'gpgv':'gpgv', 'chroot':'coreutils', 'wget':'wget', 'perl':'perl',
                 'ar':'binutils', 'xzcat':'xz-utils', 'zstdcat':'zstd', 'tar':'tar', 'gzip':'gzip'}


def ensure_host_tools():
    missing = {package for tool, package in HOST_PACKAGES.items() if not shutil.which(tool)}
    if missing:
        print('Chuẩn bị công cụ cài đặt trên USB cứu hộ...', flush=True)
        env = dict(os.environ, DEBIAN_FRONTEND='noninteractive')
        if shutil.which('apt-get'):
            subprocess.run(['apt-get', 'update'], env=env, check=True)
            command = ['apt-get', 'install', '-y', 'ca-certificates', *sorted(missing)]
        elif shutil.which('dnf'):
            translated = {'fdisk':'util-linux', 'udev':'systemd-udev', 'gpgv':'gnupg2', 'xz-utils':'xz'}
            command = ['dnf', 'install', '-y', 'ca-certificates', *sorted({translated.get(p,p) for p in missing})]
        elif shutil.which('pacman'):
            translated = {'fdisk':'util-linux', 'udev':'systemd', 'gpgv':'gnupg', 'xz-utils':'xz'}
            command = ['pacman', '-S', '--needed', '--noconfirm', 'ca-certificates', *sorted({translated.get(p,p) for p in missing})]
        else:
            raise ValueError('USB cứu hộ không có APT/DNF/pacman và thiếu công cụ: ' + ', '.join(sorted(missing)))
        subprocess.run(command, env=env, check=True)
    absent = [tool for tool in HOST_PACKAGES if not shutil.which(tool)]
    if absent:
        raise ValueError('Không chuẩn bị được công cụ: ' + ', '.join(absent))


def download(url, limit=16 * 1024**2):
    if not url.startswith('https://deb.debian.org/debian/'):
        raise ValueError('Bootstrap tools must use the official HTTPS Debian archive.')
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Downloaded bootstrap file exceeds the expected size.')
    return data


def unpack_deb(data, destination):
    if not data.startswith(b'!<arch>\n'):
        raise ValueError('Not a Debian archive')
    position = 8
    while position + 60 <= len(data):
        header = data[position:position + 60]
        if header[58:60] != b'`\n':
            raise ValueError('Malformed Debian archive header')
        size = int(header[48:58].strip())
        name = header[:16].decode('ascii').strip().rstrip('/')
        position += 60
        content = data[position:position + size]
        if len(content) != size:
            raise ValueError('Truncated Debian archive')
        position += size + size % 2
        if name.startswith('data.tar.'):
            with tarfile.open(fileobj=io.BytesIO(content), mode='r:*') as archive:
                # Signed hash manifest below pins the payload; still reject path escapes.
                if not hasattr(tarfile, 'data_filter'):
                    raise ValueError('Rescue Python needs current security updates for safe archive extraction.')
                archive.extractall(destination, filter='data')
            return
    raise ValueError('No data archive in Debian package')


def prepare(destination, suite):
    destination = Path(destination)
    manifest = json.loads((HERE / 'bootstrap-tools.json').read_text())
    for name, record in manifest.items():
        print('Xác thực công cụ ' + name + ' ' + record['version'] + '...', flush=True)
        data = download('https://deb.debian.org/debian/' + record['filename'])
        if hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError('Debian package checksum mismatch: ' + name)
        unpack_deb(data, destination)
    bootstrap = destination / 'usr/sbin/debootstrap'
    keyring = destination / 'usr/share/keyrings/debian-archive-keyring.gpg'
    if not bootstrap.is_file() or not keyring.is_file():
        raise ValueError('Bootstrap package contents are incomplete.')
    release = destination / 'InRelease'
    release.write_bytes(download('https://deb.debian.org/debian/dists/' + suite + '/InRelease'))
    subprocess.run(['gpgv', '--keyring', str(keyring), str(release)], check=True)
    return bootstrap, keyring, dict(os.environ, DEBOOTSTRAP_DIR=str(destination / 'usr/share/debootstrap'))
