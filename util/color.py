from dataclasses import dataclass

@dataclass(repr=True, eq=True)
class HexColor:
    hex: str

    def to_rgba(self) -> str:
        bytes = [int(self.hex[i:i+2], 16) for i in range(0, 6, 2)]
        r, g, b, a = bytes
        return RGBAColor(r, g, b, a)
        
@dataclass(repr=True, eq=True)
class RGBAColor:
    r: int
    g: int
    b: int
    a: int = 255
        
    @classmethod
    def from_hsv(cls, hsv: 'HSVColor') -> 'RGBColor':
        return hsv.to_rgb()

    @classmethod
    def from_hex(cls, hex: str) -> 'RGBColor':
        return cls(*hex.to_rgba())

@dataclass(repr=True, eq=True)
class RGBColor(RGBAColor):
    def __post_init__(self):
        self.a = 255

    def to_hsv(self) -> 'HSVColor':
        '''Goes from (0~255, 0~255, 0~255) to (0~360, 0~255, 0~255)'''
        r, g, b = self.r, self.g, self.b
        max_ = max(r, g, b)
        min_ = min(r, g, b)
        h = 0
        s = 0
        v = max_
        d = max_ - min_
        if max_ != 0:
            s = d / max_
        if d != 0:
            if r == max_:
                h = (g - b) / d
            elif g == max_:
                h = 2 + (b - r) / d
            elif b == max_:
                h = 4 + (r - g) / d
            h *= 60
            if h < 0:
                h += 360
        return HSVColor(h, s, v)

    @classmethod
    def from_hex(cls, hex: str) -> 'RGBColor':
        return cls(*hex.to_rgba()[:3])

@dataclass(repr=True, eq=True)
class HSVColor:
    h: float
    s: float
    v: float

    def to_rgb(self) -> 'RGBColor':
        '''Goes from (0~360, 0~255, 0~255) to (0~255, 0~255, 0~255)'''
        h, s, v = self.h, self.s, self.v
        if s == 0:
            return RGBColor(v, v, v)
        i = int(h / 60)
        f = h / 60 - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        if i == 0:
            return RGBColor(v, t, p)
        elif i == 1:
            return RGBColor(q, v, p)
        elif i == 2:
            return RGBColor(p, v, t)
        elif i == 3:
            return RGBColor(p, q, v)
        elif i == 4:
            return RGBColor(t, p, v)
        else:
            return RGBColor(v, p, q)

    @classmethod
    def from_rgb(cls, rgb: 'RGBColor') -> 'HSVColor':
        return rgb.to_hsv()

# Unit tests
import unittest

class TestHSVColor(unittest.TestCase):
    def test_to_rgb(self):
        hsv = HSVColor(0, 255, 255) # red
        rgb = hsv.to_rgb()
        self.assertEqual(rgb, RGBColor(255, 0, 0))

    def test_from_rgb(self):
        rgb = RGBColor(145, 68, 91)
        hsv = HSVColor.from_rgb(rgb)
        self.assertEqual(hsv, HSVColor(342, 53, 57))


if __name__ == "__main__":
    unittest.main()