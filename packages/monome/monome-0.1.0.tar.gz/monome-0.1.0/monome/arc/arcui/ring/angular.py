from .base import ArcUIRing
from ..page import ArcUIPage
from ....utils import round_to_integer
import numpy as np

class ArcUIRingAngular (ArcUIRing):
    @property
    def normalise(self):
        return False

    def draw(self):
        position = round_to_integer(self.position) % self.led_count        
        display = [0] * self.led_count
        display[position] = self.led_intensity_cursor
        self.arc.ring_map(self.index, display)

    def _handle_enc_delta(self, delta: float):
        self.position = (self.position + delta) % self.led_count
        delta_radians = (np.pi * 2) * (delta / self.led_count)
        angle_radians = (np.pi * 2) * (self.position / self.led_count)
        
        self._call_handlers(angle_radians, delta_radians)