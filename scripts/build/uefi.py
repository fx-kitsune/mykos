#!/usr/bin/env python3
"""Add unsigned amd64 UEFI removable-media boot to a completed BIOS live ISO."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def menu_from_syslinux(text):
    entries = []
    for section in re.split(r'(?m)^label ', text)[1:]:
        kernel = re.search(r'(?m)^\s+kernel (\S+)\s*$', section)
        append = re.search(r'(?m)^\s+append (.+)$', section)
        if not kernel or not append:
            raise ValueError('Incomplete BIOS entry; refusing a mismatched EFI menu')
        tokens = append[1].split()
        initrds = [token[7:] for token in tokens if token.startswith('initrd=')]
        arguments = [token for token in tokens if not token.startswith('initrd=')]
        if len(initrds) != 1 or 'boot=casper' not in arguments:
            raise ValueError('Expected exactly one initrd and a Casper live entry')
        for token in [kernel[1], *initrds, *arguments]:
            if not re.fullmatch(r'[A-Za-z0-9_./=,:+\-]+', token):
                raise ValueError('Unsupported token in boot menu')
        if not all(re.fullmatch(r'/casper/[A-Za-z0-9_.+\-]+', path)
                   for path in [kernel[1], initrds[0]]):
            raise ValueError('Kernel/initrd must be files directly in /casper')
        title = re.search(r'(?m)^\s+menu label (.+)$', section)
        if not title or not re.fullmatch(r'[A-Za-z0-9 ()/\-]+', title[1]):
            raise ValueError('Unsupported menu title')
        entries.append((title[1], kernel[1], initrds[0], arguments))
    if len(entries) != 3:
        raise ValueError('Expected normal, safe and software live entries')
    lines = ['set default=0', 'set timeout=5']
    for title, kernel, initrd, arguments in entries:
        lines += [f"menuentry '{title}' {{", f"  linux {kernel} {' '.join(arguments)}",
                  f'  initrd {initrd}', '}']
    return '\n'.join(lines) + '\n', entries


def add_uefi(iso, tree, destination):
    iso, tree, destination = map(lambda path: Path(path).resolve(), (iso, tree, destination))
    if not iso.is_file() or destination.exists() or destination == iso:
        raise ValueError('Require an existing source ISO and a new output path')
    menu, entries = menu_from_syslinux((tree / 'isolinux/isolinux.cfg').read_text())
    for _, kernel, initrd, _ in entries:
        for name in [kernel, initrd]:
            if not (tree / name.lstrip('/')).is_file():
                raise ValueError('Missing boot payload: ' + name)
    with tempfile.TemporaryDirectory(prefix='mykos-uefi-', dir=destination.parent) as temp:
        stage = Path(temp)
        config = stage / 'grub.cfg'
        config.write_text(menu)
        early = stage / 'early.cfg'
        early.write_text('search --no-floppy --file --set=root /.disk/mykos-uefi\n'
                         'configfile /boot/grub/grub.cfg\n')
        marker = stage / 'mykos-uefi'
        marker.write_text('MyKOS amd64 live media\n')
        efi = stage / 'BOOTX64.EFI'
        subprocess.run(['grub-mkstandalone', '-O', 'x86_64-efi', '--locales=', '--fonts=',
                        '--modules=part_gpt part_msdos fat iso9660 search search_fs_file normal linux configfile',
                        '-o', str(efi), 'boot/grub/grub.cfg=' + str(early)], check=True)
        if efi.read_bytes()[:2] != b'MZ':
            raise ValueError('GRUB did not produce a PE/COFF EFI executable')
        esp = stage / 'efi.img'
        with esp.open('wb') as stream:
            # FAT16 is supported on EFI removable media. Keep the image below
            # El Torito's 16-bit sector-count limit (a 64 MiB image wraps to zero).
            stream.truncate(16 * 1024**2)
        subprocess.run(['mformat', '-i', str(esp), '-v', 'MYKOS_EFI', '::'], check=True)
        subprocess.run(['mmd', '-i', str(esp), '::/EFI', '::/EFI/BOOT'], check=True)
        subprocess.run(['mcopy', '-i', str(esp), str(efi), '::/EFI/BOOT/BOOTX64.EFI'], check=True)
        # Replay the working BIOS El Torito entry, append a real GPT ESP for USB,
        # and register that same FAT image as the EFI El Torito boot image.
        subprocess.run(['xorriso', '-indev', str(iso), '-outdev', str(destination),
                        '-boot_image', 'any', 'replay',
                        '-map', str(config), '/boot/grub/grub.cfg',
                        '-map', str(efi), '/EFI/BOOT/BOOTX64.EFI',
                        '-map', str(marker), '/.disk/mykos-uefi',
                        '-append_partition', '2', '0xef', str(esp),
                        '-boot_image', 'any', 'appended_part_as=gpt',
                        '-boot_image', 'any', 'next',
                        '-boot_image', 'any', 'efi_path=--interval:appended_partition_2:all::',
                        '-boot_image', 'any', 'platform_id=0xef',
                        '-boot_image', 'any', 'emul_type=no_emulation', '-commit'], check=True)
        result = subprocess.run(['xorriso', '-indev', str(destination),
                                 '-report_el_torito', 'plain', '-report_system_area', 'plain'],
                                check=True, text=True, capture_output=True)
        report = result.stdout + result.stderr
        if not all(word in report for word in ['UEFI', 'BIOS', 'GPT']):
            raise ValueError('Missing BIOS/UEFI/GPT boot structures in completed ISO')
        destination.with_suffix('.boot-layout.txt').write_text(report)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('tree', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    add_uefi(args.iso, args.tree, args.output)
