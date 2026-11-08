"""Recorded PCM must contain the requested tone; process success or silence is insufficient."""
import importlib.util
import math
from pathlib import Path
import struct
import tempfile
import unittest
import wave

SCRIPTS = Path(__file__).resolve().parents[2] / 'scripts/testing'
spec = importlib.util.spec_from_file_location('audio_evidence', SCRIPTS / 'multimedia_probe.py')
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)


class AudioEvidenceTests(unittest.TestCase):
    def recorded(self, frequency, rate=48000):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'capture.wav'
            with wave.open(str(path), 'wb') as output:
                output.setnchannels(2); output.setsampwidth(2); output.setframerate(rate)
                output.writeframes(b''.join(struct.pack('<hh', value, value) for value in
                    [round(6000 * math.sin(2 * math.pi * frequency * frame / rate)) for frame in range(rate // 2)]))
            return audio.analyze_wave(path)

    def test_requested_tone_is_detected_at_native_and_resampled_rates(self):
        for rate in [48000, 44100]:
            self.assertTrue(self.recorded(440, rate)['tone_detected'])

    def test_silence_and_unrelated_sound_do_not_pass(self):
        self.assertFalse(self.recorded(0)['tone_detected'])
        self.assertFalse(self.recorded(880)['tone_detected'])
