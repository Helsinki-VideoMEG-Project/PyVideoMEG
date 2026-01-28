"""Wrapper functions for command-line scripts."""

import importlib.util
import os


def _load_script_main(script_name):
    """Load a script and return its main function."""
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "bin", script_name + ".py"
    )
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


def pvm_repack_audio_main():
    """Entry point for pvm_repack_audio command."""
    _load_script_main("pvm_repack_audio")()


def pvm_show_info_main():
    """Entry point for pvm_show_info command."""
    _load_script_main("pvm_show_info")()


def pvm_repair_main():
    """Entry point for pvm_repair command."""
    _load_script_main("pvm_repair")()


def pvm_export_audio_main():
    """Entry point for pvm_export_audio command."""
    _load_script_main("pvm_export_audio")()


def pvm_data_converter0_1_main():
    """Entry point for pvm_data_converter0_1 command."""
    _load_script_main("pvm_data_converter0_1")()


def pvm_export_dragdrop_main():
    """Entry point for pvm_export_dragdrop command."""
    _load_script_main("pvm_export_dragdrop")()


def pvm_merge_main():
    """Entry point for pvm_merge command."""
    _load_script_main("pvm_merge")()


def pvm_export_main():
    """Entry point for pvm_export command."""
    _load_script_main("pvm_export")()
