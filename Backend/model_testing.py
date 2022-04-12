import unittest
import models


class MyTestCase(unittest.TestCase):
    def test_recallFunc(self):
        arr = ["diabetes, qcsi"]
        for i in arr:
            self.assertEqual(getattr(i.predict(),))
        self.assertEqual(getattr())  # add assertion here


if __name__ == '__main__':
    unittest.main()
