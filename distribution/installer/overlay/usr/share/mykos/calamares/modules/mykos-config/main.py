"""Hoàn tất riêng bản cài; không sửa môi trường live hoặc dữ liệu người dùng."""
import configparser
from pathlib import Path
import shutil

SOFTWARE_FLAGS = ('systemd.setenv=QT_QUICK_BACKEND=software',)


def target_path(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError('Đường dẫn đích đi qua liên kết ra ngoài bản cài: ' + relative)
    return path


def configure_target(root, software=False):
    root = Path(root)
    if not root.is_absolute() or root.resolve() == Path('/') or not root.is_dir():
        raise ValueError('Cần thư mục đích cài đặt đã gắn, khác thư mục gốc của môi trường live.')
    root = root.resolve()
    for relative in ('usr/bin/mykos-install', 'usr/share/applications/mykos-install.desktop',
                     'etc/sudoers.d/casper', 'etc/sudoers.d/99-casper',
                     'etc/sudoers.d/live', 'etc/sudoers.d/live-config',
                     'usr/lib/live/config/0099-mykos-session'):
        target_path(root, relative).unlink(missing_ok=True)
    sddm = target_path(root, 'etc/sddm.conf')
    if sddm.is_file():
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        config.read(sddm)
        config.remove_section('Autologin')
        with sddm.open('w') as stream:
            config.write(stream)
    installer_config = target_path(root, 'etc/calamares')
    if installer_config.exists():
        shutil.rmtree(installer_config)
    if software:
        path = target_path(root, 'etc/default/grub.d/60-mykos-software.cfg')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('# Giữ chế độ đồ họa phần mềm đã chọn ở phiên live.\n'
                        'GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT '
                        + ' '.join(SOFTWARE_FLAGS) + '"\n')
        path.chmod(0o644)


def pretty_name():
    return 'Hoàn tất cấu hình bản cài MyKOS'


def run():
    import libcalamares
    try:
        root = libcalamares.globalstorage.value('rootMountPoint')
        command_line = Path('/proc/cmdline').read_text().split()
        configure_target(root, software=all(flag in command_line for flag in SOFTWARE_FLAGS))
    except (OSError, TypeError, ValueError) as error:
        return ('Không hoàn tất được cấu hình MyKOS', str(error))
    return None
