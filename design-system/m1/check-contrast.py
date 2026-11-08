#!/usr/bin/env python3
"""Kiểm tra tương phản chữ trong giá trị thiết kế M1, không cần thư viện ngoài."""
import json
from pathlib import Path


def luminance(color):
    values = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    return sum((v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4) * weight
               for v, weight in zip(values, (.2126, .7152, .0722)))


def contrast(a, b):
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + .05) / (lo + .05)


if __name__ == '__main__':
    data = json.loads(Path(__file__).with_name('tokens.json').read_text())
    failures = []
    for mode, colors in data['color'].items():
        for foreground, background in [('text', 'background'), ('text', 'surface'),
                                       ('muted', 'background'), ('muted', 'surface'),
                                       ('accent', 'background'), ('onAccent', 'accent'),
                                       ('danger', 'surface')]:
            ratio = contrast(colors[foreground], colors[background])
            print(f'{mode}: {foreground}/{background} = {ratio:.2f}:1')
            if ratio < 4.5:
                failures.append((mode, foreground, background))
    if failures:
        raise SystemExit(f'Cặp màu chưa đạt tương phản 4,5:1: {failures}')
    print('Tất cả cặp màu chữ được kiểm tra đều đạt ít nhất 4,5:1.')
