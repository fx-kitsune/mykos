"""Chạy mã bố cục thực với API Plasma giả để kiểm tra quy tắc hồ sơ mới."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'distribution/branding/overlay/usr/share/plasma/look-and-feel/org.mykos.desktop'
LAYOUT = PACKAGE / 'contents/layouts/org.kde.plasma.desktop-layout.js'


@unittest.skipUnless(shutil.which('node'), 'Cần Node.js để kiểm tra mã bố cục Plasma')
class PlasmaLayoutTests(unittest.TestCase):
    def evaluate(self, count):
        harness = '''
const fs = require('fs'), vm = require('vm');
const created = [];
function Panel() {
  this.widgets = [];
  this.addWidget = function(id) {
    const widget = {id,config:{},writeConfig(key,value){this.config[key]=value;}};
    this.widgets.push(widget); return widget;
  };
  created.push(this);
}
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'), {panels:()=>Array(Number(process.argv[2])).fill({}),Panel});
console.log(JSON.stringify(created));
'''
        result = subprocess.run(['node', '-e', harness, str(LAYOUT), str(count)],
                                capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def test_new_profile_gets_one_bottom_panel_without_workspace(self):
        panels = self.evaluate(0)
        self.assertEqual(len(panels), 1)
        self.assertEqual(panels[0]['location'], 'bottom')
        self.assertEqual(panels[0]['height'], 48)
        widgets = panels[0]['widgets']
        self.assertEqual([item['id'] for item in widgets], [
            'org.kde.plasma.kickoff', 'org.kde.plasma.icontasks',
            'org.kde.plasma.systemtray', 'org.kde.plasma.digitalclock', 'org.kde.plasma.showdesktop'])
        self.assertEqual(widgets[1]['config']['launchers'], ['applications:org.kde.dolphin.desktop'])
        self.assertEqual(json.loads((PACKAGE / 'metadata.json').read_text())['KPlugin']['Id'], 'org.mykos.desktop')

    def test_existing_panels_are_not_replaced_or_duplicated(self):
        self.assertEqual(self.evaluate(1), [])
        self.assertEqual(self.evaluate(2), [])
