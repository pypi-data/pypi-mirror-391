import unittest

import hypothesis.strategies as st
from hypothesis import given

from pycint import lib


class TestCintLen(unittest.TestCase):
    @given(ang=st.integers(0, 10))
    def test_CINTlen_cart(self, ang: int) -> None:
        self.assertEqual(lib.CINTlen_cart(ang), (ang + 1) * (ang + 2) // 2)
