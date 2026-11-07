#!/bin/bash
# Thu thập tệp chẩn đoán đã chọn; không xuất biến môi trường hoặc thông tin xác thực.
set -euo pipefail
: "${BUILD_DIRECTORY:?}"
: "${DIAGNOSTIC_DIRECTORY:?}"
mkdir -p "$DIAGNOSTIC_DIRECTORY"
if sudo test -f "$BUILD_DIRECTORY/build.log"; then
    sudo cat "$BUILD_DIRECTORY/build.log" > "$DIAGNOSTIC_DIRECTORY/build.log"
    tail -n 160 "$DIAGNOSTIC_DIRECTORY/build.log"
fi
for name in bootstrap chroot binary common; do
    if sudo test -f "$BUILD_DIRECTORY/config/$name"; then
        sudo cat "$BUILD_DIRECTORY/config/$name" > "$DIAGNOSTIC_DIRECTORY/live-build-$name.conf"
    fi
done
if sudo test -f "$BUILD_DIRECTORY/mykos-build.json"; then
    sudo cat "$BUILD_DIRECTORY/mykos-build.json" > "$DIAGNOSTIC_DIRECTORY/mykos-build.json"
fi
git rev-parse HEAD > "$DIAGNOSTIC_DIRECTORY/commit.txt"
df -h . > "$DIAGNOSTIC_DIRECTORY/disk-final.txt"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
        echo '## Kết quả tạo ISO MyKOS'
        printf '\nCommit: `%s`\n' "$(git rev-parse HEAD)"
        printf '\nTrạng thái bước tạo ảnh: **%s**\n' "${BUILD_RESULT:-chưa chạy}"
        echo
        echo '- ISO chỉ được tải lên khi tạo ảnh và kiểm tra mã SHA-256 thành công.'
        echo '- Nhật ký được lưu riêng, kể cả khi bước tạo ảnh thất bại.'
        echo '- Thời hạn lưu sản phẩm: 7 ngày; tải về trước khi hết hạn.'
        echo '- Kết quả này chưa xác nhận ISO khởi động, cài đặt hoặc đăng nhập được.'
    } >> "$GITHUB_STEP_SUMMARY"
fi
