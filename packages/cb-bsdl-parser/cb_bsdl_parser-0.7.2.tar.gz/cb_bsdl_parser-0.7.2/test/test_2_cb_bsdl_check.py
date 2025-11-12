import sys
from cb_bsdl_tools.cb_bsdl_check import main


class Test_cb_bsdl_check_functions:
    def test_main_exists(self):
        assert callable(main)


class Test_cb_bsdl_check_usage:
    def test_main_usage_no_args(self, capsys):
        test_args = ['cb_bsdl_check.py']
        sys.argv = test_args

        try:
            main()
        except SystemExit as e:
            assert e.code == 1

        captured = capsys.readouterr()
        assert 'usage:' in captured.out
