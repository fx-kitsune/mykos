#!/usr/bin/env python3
"""Export the original Fold assets to Qt-compatible SVGs and KDE icon names."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "distribution/branding/overlay"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ALIASES = {"files": ["system-file-manager", "org.kde.dolphin"],
           "terminal": ["utilities-terminal", "org.kde.konsole"],
           "settings": ["preferences-system", "systemsettings"],
           "notes": ["accessories-text-editor", "org.kde.kate"],
           "photos": ["gwenview", "org.kde.gwenview"],
           "browser": ["web-browser"]}


def flatten_svg(source):
    tree = ET.fromstring(source)
    # Qt SVG Tiny does not draw nested svg viewports. Preserve original geometry
    # using an equivalent affine group, retaining color/stroke attributes.
    for nested in list(tree):
        if nested.tag == f"{{{NS}}}svg":
            x, y = float(nested.get("x", 0)), float(nested.get("y", 0))
            vx, vy, vw, vh = map(float, nested.get("viewBox").split())
            sx, sy = float(nested.get("width")) / vw, float(nested.get("height")) / vh
            group = ET.Element(f"{{{NS}}}g", {k: v for k, v in nested.attrib.items()
                               if k not in {"x", "y", "width", "height", "viewBox"}})
            group.set("transform", f"translate({x:g} {y:g}) scale({sx:g} {sy:g}) translate({-vx:g} {-vy:g})")
            group.extend(list(nested))
            tree.remove(nested)
            tree.append(group)
    return ET.tostring(tree, encoding="unicode") + "\n"


def outputs():
    result = {}
    theme = OVERLAY / "usr/share/icons/MyKOSFold"
    result[theme / "index.theme"] = """[Icon Theme]
Name=MyKOS Fold
Comment=Original MyKOS Fold icons with Breeze fallback
Inherits=breeze,hicolor
Directories=scalable/apps,scalable/actions

[scalable/apps]
Size=96
Type=Scalable
MinSize=16
MaxSize=256
Context=Applications

[scalable/actions]
Size=24
Type=Scalable
MinSize=16
MaxSize=64
Context=Actions
"""
    for source in sorted((ROOT / "design-system/assets/app-icons").glob("*.svg")):
        svg = flatten_svg(source.read_text())
        result[ROOT / "desktop/workspace/assets" / source.name] = svg
        for name in [f"mykos-{source.stem}", *ALIASES[source.stem]]:
            result[theme / "scalable/apps" / f"{name}.svg"] = svg
    for source in sorted((ROOT / "design-system/assets/icons").glob("*.svg")):
        if source.stem != "sprite":
            result[theme / "scalable/actions" / f"mykos-{source.name}"] = source.read_text()
    mark = (ROOT / "design-system/assets/icons/mark.svg").read_text()
    for mode, color in [("dark", "#d7ef83"), ("light", "#526a2b")]:
        result[ROOT / "desktop/workspace/assets" / f"mark-{mode}.svg"] = mark.replace("currentColor", color)
    result[ROOT / "distribution/installer/overlay/etc/calamares/branding/mykos/logo.svg"] = mark.replace("currentColor", "#d7ef83")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, value in outputs().items():
        if args.check:
            if not path.exists() or path.read_text() != value:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
    if stale:
        parser.exit(1, "Stale design exports:\n" + "\n".join(stale) + "\n")
