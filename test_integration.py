import subprocess
import sys
import unittest

class TestAppInput(unittest.TestCase):
    # test case to run authorizer app and pass file with operations, parse application output and assert with desired output file in the end.
    def test_app_input_run(self):
        with open("operations_complex", "r") as data:
            result = subprocess.run([sys.executable, "app.py"], input=data.read(), capture_output=True, text=True)
        with open("operations_complex_output", "r") as expected_result:
            assert expected_result.read() == result.stdout


if __name__ == '__main__':
    unittest.main()
