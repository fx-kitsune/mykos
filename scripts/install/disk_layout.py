"""Read-only disk discovery and explicit whole-disk layout operations.

No commands that write a disk run during discovery, plan generation or selection.
Disk preparation is callable only with a revalidated, explicitly confirmed disk.
"""
import json
import fcntl
import os
from pathlib import Path
import stat
import subprocess
import struct
import time

MINIMUM_BYTES = 25 * 1024**3
EFI_TYPE = 'c12a7328-f81f-11d2-ba4b-00a0c93ec93b'
BIOS_TYPE = '21686148-6449-6e6f-744e-656564454649'
ROOT_TYPE = '0fc63daf-8483-4772-8e79-3d69d8477de4'
CONFIRMATION = 'XOA VA CAI MYKOS'
COLUMNS = 'NAME,PATH,MAJ:MIN,TYPE,SIZE,MODEL,SERIAL,WWN,TRAN,RM,RO,FSTYPE,MOUNTPOINTS,PKNAME,LOG-SEC'
CRITICAL = {'/', '/boot', '/boot/efi', '/usr', '/var', '/home', '/run', '/cdrom', '/isodevice', '/cow', '/rofs'}
LIVE_PREFIXES = ('/run/live', '/lib/live/mount', '/run/archiso', '/run/miso', '/run/initramfs')


def loop_backing_device(path):
    """Ask the kernel: backing_file paths may belong to the initramfs namespace."""
    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC)
    try:
        info = bytearray(232)  # struct loop_info64
        fcntl.ioctl(fd, 0x4C05, info, True)  # LOOP_GET_STATUS64, read-only
        device = struct.unpack_from('=Q', info)[0]
        # lo_device uses the kernel's new_encode_dev, not libc's dev_t layout.
        return f'{(device >> 8) & 0xfff}:{(device & 0xff) | ((device >> 12) & 0xfff00)}'
    finally:
        os.close(fd)


def run(argv, **kwargs):
    return subprocess.run(argv, text=True, check=True, **kwargs)


def output(argv):
    return run(argv, capture_output=True).stdout.strip()


def flatten(rows):
    for row in rows:
        yield row
        yield from flatten(row.get('children', []))


def graph(rows):
    nodes, owners = {}, {}
    def visit(row, ancestors):
        identifier = row['maj:min']
        nodes[identifier] = row
        parents = ancestors | ({identifier} if row['type'] == 'disk' else set())
        owners.setdefault(identifier, set()).update(parents)
        for child in row.get('children', []):
            visit(child, parents)
    for row in rows:
        visit(row, set())
    return nodes, owners


def is_critical_mount(target, paths):
    path = Path(target)
    return (target in CRITICAL or target.startswith(LIVE_PREFIXES)
            or any(p == path or p.is_relative_to(path) for p in paths))


def protected_disks(nodes, owners, mounts, paths, backing_file=None, source_for_path=None):
    """Include loop-backed rescue ISOs, not just devices mounted at /."""
    def loop_backing(identifier):
        path = Path('/sys/dev/block') / identifier / 'loop/backing_file'
        return path.read_text().strip() if path.is_file() else None
    kernel_backing = backing_file is None
    backing_file = backing_file or loop_backing
    def filesystem_for(path):
        data = json.loads(output(['findmnt', '--json', '--target', path, '--output', 'MAJ:MIN']))
        return data['filesystems'][0]['maj:min']
    source_for_path = source_for_path or filesystem_for
    def resolve(identifier, seen):
        if identifier in seen:
            raise ValueError('Không xác định an toàn được ổ chứa môi trường đang chạy (vòng lặp thiết bị).')
        if owners.get(identifier):
            return owners[identifier]
        node = nodes.get(identifier, {})
        if node.get('type') == 'loop' and kernel_backing:
            try:
                device = loop_backing_device(node.get('path') or '/dev/block/' + identifier)
            except OSError:
                pass  # Older/restricted rescue hosts can still expose a usable file path.
            else:
                if not device.startswith('0:'):
                    return resolve(device, seen | {identifier})
        backing = backing_file(identifier)
        if backing:
            path = backing if backing.startswith('/') else '/' + backing
            return resolve(source_for_path(path), seen | {identifier})
        if node.get('type') == 'loop':
            raise ValueError('Không xác định được ổ chứa ISO cứu hộ; chưa thể chọn ổ để xóa.')
        if identifier.startswith('0:') or node.get('type') in {'rom', 'zram'}:
            return set()  # overlay/tmpfs/network mounts or read-only optical media
        raise ValueError('Thiếu thông tin ổ của một filesystem đang sử dụng: ' + identifier)
    protected = set()
    for row in flatten(mounts):
        if is_critical_mount(row['target'], paths):
            protected.update(resolve(row['maj:min'], set()))
            # Persistent live systems can keep overlay writes on an internal
            # disk even when / itself has an anonymous 0:* filesystem ID.
            if row.get('fstype') == 'overlay':
                backing_paths = []
                for option in row.get('options', '').split(','):
                    key, _, value = option.partition('=')
                    if key in {'upperdir', 'workdir', 'lowerdir'}:
                        backing_paths.extend(value.split(':'))
                if not backing_paths:
                    raise ValueError('Không xác định được filesystem nền của hệ thống live overlay.')
                for path in backing_paths:
                    protected.update(resolve(source_for_path(path), {row['maj:min']}))
    # Also guard critical mountpoints listed by lsblk if mount inventory is incomplete.
    for identifier, node in nodes.items():
        for mount in node.get('mountpoints') or []:
            if mount and not mount.startswith('[') and is_critical_mount(mount, paths):
                protected.update(resolve(identifier, set()))
    return protected


def identity(disk):
    return {key: disk.get(key) for key in ['path', 'maj:min', 'size', 'serial', 'wwn', 'model', 'log-sec']}


def assess(rows, mounts, paths, backing_file=None, source_for_path=None):
    nodes, owners = graph(rows)
    protected = protected_disks(nodes, owners, mounts, paths, backing_file, source_for_path)
    candidates, excluded = [], []
    for disk in nodes.values():
        if disk['type'] != 'disk':
            continue
        reason = None
        identifier = disk['maj:min']
        descendants = [row for key, row in nodes.items() if identifier in owners.get(key, set()) and key != identifier]
        if disk.get('ro'):
            reason = 'ổ chỉ đọc'
        elif disk.get('rm') or disk.get('tran') == 'usb':
            reason = 'ổ rời/USB (không chọn làm ổ cài tự động)'
        elif identifier in protected:
            reason = 'đang chứa hệ thống, dữ liệu chạy hoặc môi trường cứu hộ'
        elif any(row['type'] != 'part' for row in descendants):
            reason = 'đang có thiết bị LVM/RAID/mã hóa hoạt động'
        elif int(disk.get('size') or 0) < MINIMUM_BYTES:
            reason = 'dung lượng dưới 25 GiB'
        elif not (disk.get('serial') or disk.get('wwn')):
            reason = 'không có mã nhận diện ổ ổn định'
        if reason:
            excluded.append({'path': disk['path'], 'reason': reason})
        else:
            candidates.append(disk)
    candidates.sort(key=lambda d: (d.get('tran') != 'nvme', d['path']))
    return candidates, excluded, nodes, owners


def scan(paths):
    disks = json.loads(output(['lsblk', '--json', '--bytes', '--paths', '--output', COLUMNS]))['blockdevices']
    mounts = json.loads(output(['findmnt', '--json', '--output', 'TARGET,SOURCE,MAJ:MIN,FSTYPE,OPTIONS']))['filesystems']
    candidates, excluded, nodes, owners = assess(disks, mounts, paths)
    return {'candidates': candidates, 'excluded': excluded, 'nodes': nodes, 'owners': owners, 'mounts': mounts}


def selected(path, paths, expected=None):
    snapshot = scan(paths)
    canonical = str(Path(path).resolve())
    disk = next((d for d in snapshot['candidates'] if str(Path(d['path']).resolve()) == canonical), None)
    if disk is None:
        raise ValueError('Ổ đã chọn không còn đủ điều kiện an toàn để cài: ' + str(path))
    if expected is not None and identity(disk) != expected:
        raise ValueError('Thông tin ổ đã thay đổi từ lúc xác nhận; dừng trước khi ghi.')
    if not stat.S_ISBLK(Path(disk['path']).stat().st_mode):
        raise ValueError('Ổ đích không phải block device.')
    return disk, snapshot


def layout(mode):
    if mode not in {'bios', 'uefi'}:
        raise ValueError('Unsupported boot mode')
    first = (f'size=512M, type={EFI_TYPE}, name="MyKOS EFI"' if mode == 'uefi' else
             f'size=2M, type={BIOS_TYPE}, name="MyKOS BIOS"')
    return f'label: gpt\n{first}\ntype={ROOT_TYPE}, name="MyKOS root"\n'


def describe(disk, mode):
    return {'disk': disk['path'], 'model': (disk.get('model') or '').strip(),
            'serial': disk.get('serial'), 'size_gib': round(int(disk['size']) / 1024**3, 1),
            'boot_mode': mode, 'erases_entire_disk': True,
            'current_partitions': [{'path': row['path'], 'fstype': row.get('fstype'),
                                    'size_gib': round(int(row.get('size') or 0) / 1024**3, 1)}
                                   for row in flatten(disk.get('children', []))],
            'new_layout': ['EFI 512 MiB (FAT32)' if mode == 'uefi' else 'BIOS boot 2 MiB',
                           'MyKOS root: remaining space (ext4)']}


def release_mounts(disk, snapshot):
    """Stop on busy targets. Never use force/lazy unmount or kill user processes."""
    owner = disk['maj:min']
    for row in flatten(snapshot['mounts']):
        if owner not in snapshot['owners'].get(row['maj:min'], set()):
            continue
        for child in flatten(row.get('children', [])):
            if owner not in snapshot['owners'].get(child['maj:min'], set()):
                raise ValueError('Có filesystem của ổ khác lồng trong ổ đích; không thể tự tháo an toàn.')
    for line in Path('/proc/swaps').read_text().splitlines()[1:]:
        name = line.split()[0]
        if name.startswith('/dev/'):
            device = os.stat(name).st_rdev
            key = f'{os.major(device)}:{os.minor(device)}'
        else:
            data = json.loads(output(['findmnt', '--json', '--target', name, '--output', 'MAJ:MIN']))
            key = data['filesystems'][0]['maj:min']
        if owner in snapshot['owners'].get(key, set()):
            run(['swapoff', name])
    targets = {row['target'] for row in flatten(snapshot['mounts'])
               if owner in snapshot['owners'].get(row['maj:min'], set())}
    for target in sorted(targets, key=lambda p: len(Path(p).parts), reverse=True):
        run(['umount', target])


def prepare(disk, mode, paths):
    """Called after confirmation and password entry; recheck before the first write."""
    expected = identity(disk)
    current, snapshot = selected(disk['path'], paths, expected)
    release_mounts(current, snapshot)
    current, snapshot = selected(disk['path'], paths, expected)
    if any(current['maj:min'] in snapshot['owners'].get(row['maj:min'], set()) for row in flatten(snapshot['mounts'])):
        raise ValueError('Ổ đích vẫn còn được mount; chưa ghi bảng phân vùng.')
    run(['sfdisk', '--wipe', 'always', '--wipe-partitions', 'always', current['path']], input=layout(mode))
    run(['udevadm', 'settle', '--timeout=30'])
    data = json.loads(output(['sfdisk', '--json', current['path']]))['partitiontable']
    parts = data.get('partitions', [])
    expected_types = [EFI_TYPE if mode == 'uefi' else BIOS_TYPE, ROOT_TYPE]
    if len(parts) != 2 or [p['type'].lower() for p in parts] != expected_types:
        raise RuntimeError('Bảng phân vùng mới không khớp kế hoạch; chưa format filesystem.')
    paths_out = [p['node'] for p in parts]
    deadline = time.monotonic() + 15
    while not all(Path(path).exists() for path in paths_out):
        if time.monotonic() > deadline:
            raise RuntimeError('Kernel chưa xuất hiện phân vùng mới; chưa format filesystem.')
        time.sleep(0.2)
    # Confirm each node really belongs to the same selected block device.
    latest = scan(paths)
    for path in paths_out:
        st = Path(path).stat()
        if not stat.S_ISBLK(st.st_mode) or latest['owners'].get(f'{os.major(st.st_rdev)}:{os.minor(st.st_rdev)}') != {current['maj:min']}:
            raise RuntimeError('Phân vùng mới không thuộc ổ đã xác nhận; chưa format.')
    selected(current['path'], paths, expected)
    if mode == 'uefi':
        run(['mkfs.fat', '-F', '32', '-n', 'MYKOS_EFI', paths_out[0]])
    selected(current['path'], paths, expected)
    run(['mkfs.ext4', '-F', '-L', 'MyKOS', paths_out[1]])
    for path in paths_out:
        run(['udevadm', 'trigger', '--action=change', '--sysname-match=' + Path(path).name])
    run(['udevadm', 'settle', '--timeout=30'])
    return paths_out[1], paths_out[0] if mode == 'uefi' else None
