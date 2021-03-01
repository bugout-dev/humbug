import unittest

from . import system_information


class TestGenerateSystemInformation(unittest.TestCase):
    def test_generate_system_information(self):
        system_information.generate()


if __name__ == "__main__":
    unittest.main()
