
import os
import glob
from pathlib import Path

from cb_bsdl_parser.cb_bsdl import CBBsdl
from cb_bsdl_parser.cb_bsdl import SkipError


class Test_verbose:
    def test_verbose_on(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'

        bsdl = CBBsdl(bsdl_file, verbose=True)

        assert bsdl.verbose, 'Verbose test completed.'

    def test_verbose_off(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, verbose=False)
        assert not bsdl.verbose, 'Verbose test completed.'

    def test_print(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'

        bsdl = CBBsdl(bsdl_file, verbose=True)
        bsdl.print_bsr_table()

        assert True, 'Print test completed.'


class Test_check_entity_name:
    def test_0_pass_entity_name(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/entity_name_test0__CortexMx.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_entity_name()

        assert True, 'Entity name check passed as expected.'

    def test_1_fail_entity_name(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/entity_name_test1__CortexMx.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_entity_name()
        except ValueError as e:
            assert 'Entity name is malformed in the BSDL content.' in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_bsr_length:
    def test_0_pass_bsr_length(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_bsr_length()

        assert True, 'BSR length check passed as expected.'

    def test_1_fail_bsr_length(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/bsr_length_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_bsr_length()
        except ValueError as e:
            assert 'BSR length not consistent' in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_ports_and_pin_map_length:
    def test_0_pass_ports_and_pin_map_length(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_ports_and_pin_map_length()

        assert True, 'Ports and pin map length check passed as expected.'

    def test_1_fail_ports_and_pin_map_length(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/' \
            'ports_and_pin_map_length_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_ports_and_pin_map_length()
        except ValueError as e:
            assert 'Port and pin map lengths are inconsistent' in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_port_to_pin_mapping:
    def test_0_pass_port_to_pin_mapping(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_port_to_pin_mapping()

        assert True, 'Port to pin mapping check passed as expected.'

    def test_1_fail_port_to_pin_mapping(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/' \
            'port_to_pin_mapping_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_port_to_pin_mapping()
        except ValueError as e:
            assert "The following ports are not mapped to any pin: ['JTRST', 'NRST_XXX']" in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_pin_to_port_mapping:
    def test_0_pass_pin_to_port_mapping(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_pin_to_port_mapping()

        assert True, 'Pin to port mapping check passed as expected.'

    def test_1_fail_pin_to_port_mapping(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/' \
            'pin_to_port_mapping_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_pin_to_port_mapping()
        except ValueError as e:
            assert "The following pins are not mapped to any port: ['56', '7']" in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_bsr_to_ports_mapping:
    def test_0_pass_bsr_to_ports_mapping(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_bsr_to_ports_mapping()

        assert True, 'BSR to ports mapping check passed as expected.'

    def test_1_fail_bsr_to_ports_mapping(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/' \
            'bsr_to_ports_mapping_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_bsr_to_ports_mapping()
        except ValueError as e:
            assert "The following BSR cells are not mapped to any port: " \
                "['PA4_in', 'PA4_out', 'PC13_XXX_out']" in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_pin_count:
    def test_0_pass_pin_count(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_pin_count()

        assert True, 'Pin count check passed as expected.'

    def test_1_fail_pin_count(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/' \
            'pin_count_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_pin_count()
        except ValueError as e:
            assert "Pin count in pin map is inconsistent: expected 64 pins, found 63 pins" in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_missing_pins:
    def test_0_pass_missing_pins(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_missing_pins()

        assert True, 'Missing pins check passed as expected.'

    def test_1_fail_missing_pins(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/pin_count_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_missing_pins()
        except ValueError as e:
            assert "Missing pin numbers in the pin map: ['23']" in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_extra_pins:
    def test_0_pass_extra_pins(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_extra_pins()

        assert True, 'Extra pins check passed as expected.'

    def test_1_fail_extra_pins(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/extra_pins_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_extra_pins()
        except ValueError as e:
            assert "Extra pin numbers in the pin map: ['65']" in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_check_double_assigned_pins:
    def test_0_pass_double_assigned_pins(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        bsdl.check_double_assigned_pins()

        assert True, 'Double assigned pins check passed as expected.'

    def test_1_fail_double_assigned_pins(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/' \
            'double_assigned_pins_test1__STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.check_double_assigned_pins()
        except ValueError as e:
            assert "Double assigned pin numbers in the pin map: ['62']" in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover


class Test_get_expected_pin_numbers:
    def test_get_expected_pin_numbers(self):
        bsdl_package_folder = Path('./test/bsdl_files/packages/')

        bsdl_patterns = [
            os.path.join(bsdl_package_folder, "*.bsd"),
            os.path.join(bsdl_package_folder, "*.bsdl"),
            os.path.join(bsdl_package_folder, "*.BSL"),
            os.path.join(bsdl_package_folder, "*.BSDL")
        ]

        bsdl_files = []
        for pattern in bsdl_patterns:
            bsdl_files.extend(glob.glob(pattern))

        if not bsdl_files:  # pragma: no cover
            assert False, 'No BSDL files found for testing expected pin numbers.'

        for bsdl_file in bsdl_files:
            bsdl = CBBsdl(bsdl_file, run_checks=False)

            expected_pins = bsdl.get_expected_pin_numbers()

            assert len(expected_pins) == len(bsdl.get_pin_map()), \
                'Expected pin numbers do not match.'

    def test_get_expected_pin_numbers_invalid_package(self):
        bsdl_file = './test/bsdl_files/packages_fail/' \
                    'STM32U535_U545_UFBGA100.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.get_expected_pin_numbers()
        except SkipError as e:
            assert 'Physical pin map UFBGA100_PACKAGE skipped' in str(e)
            return

        assert False, 'Expected SkipError was not raised.'  # pragma: no cover


class Test_port_type_not_supported:
    def test_port_type_not_supported(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/' \
                    'port_type_not_supported__STM32U575_U585_LQFP64.bsd'

        try:
            bsdl = CBBsdl(bsdl_file, run_checks=False)  # noqa: F841
        except NotImplementedError as e:
            assert "Port Type 'globi_bit' not supported yet" in str(e)
            return

        assert False, 'Expected NotImplementedError was not raised.'  # pragma: no cover


class Test_cell_desc_not_supported:
    def test_cell_desc_not_supported(self):
        bsdl_file = './test/bsdl_files/pass_fail_checks/' \
                    'cell_desc_not_supported__STM32U575_U585_LQFP64.bsd'

        try:
            bsdl = CBBsdl(bsdl_file, run_checks=False)  # noqa: F841
        except NotImplementedError as e:
            assert "Cell_func 'internal_globi' not recognized for cell_desc 'cell_354'" in str(e)
            return

        assert False, 'Expected NotImplementedError was not raised.'  # pragma: no cover


class Test_get_bsr_xxx_for_unsupported_cell:
    def test_get_bsr_data_cell(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.get_bsr_data_cell('xxx')
        except ValueError as e:
            assert "BSR cell 'xxx' not found in BSR content." in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover

    def test_get_bsr_cell_type(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.get_bsr_cell_type('xxx')
        except ValueError as e:
            assert "BSR cell 'xxx' not found in BSR content." in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover

    def test_get_bsr_cell_desc(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.get_bsr_cell_desc('xxx')
        except ValueError as e:
            assert "BSR cell 'xxx' not found in BSR content." in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover

    def test_get_bsr_cell_func(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.get_bsr_cell_func('xxx')
        except ValueError as e:
            assert "BSR cell 'xxx' not found in BSR content." in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover

    def test_get_bsr_cell_val(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.get_bsr_cell_val('xxx')
        except ValueError as e:
            assert "BSR cell 'xxx' not found in BSR content." in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover

    def test_get_bsr_ctrl_cell(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.get_bsr_ctrl_cell('xxx')
        except ValueError as e:
            assert "BSR cell 'xxx' not found in BSR content." in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover

    def test_get_bsr_disval(self):
        bsdl_file = './test/bsdl_files/STM32U575_U585_LQFP64.bsd'
        bsdl = CBBsdl(bsdl_file, run_checks=False)

        try:
            bsdl.get_bsr_disval('xxx')
        except ValueError as e:
            assert "BSR cell 'xxx' not found in BSR content." in str(e)
            return

        assert False, 'Expected ValueError was not raised.'  # pragma: no cover
