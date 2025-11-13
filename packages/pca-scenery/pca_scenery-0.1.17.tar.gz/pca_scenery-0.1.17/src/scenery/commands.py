import argparse
import os
import pathlib
import sys
import typing
import re

import dotenv

from scenery import logger, config
from scenery.common import iter_on_manifests
from scenery.cli import (
    interpret, 
    report_manifest_integration_test, 
    report_manifest_load_test,
    report_inspect,
)


########################
# SCENERY CONFIG
########################

def scenery_setup(args: argparse.Namespace) -> bool:
    """Read the settings module and set the corresponding environment variables.
    """

    config.read(args.config)
    dotenv.load_dotenv(args.env)

    logger.debug(dict(config))

    if "manifests" not in config.sections():
        raise ValueError(f"{args.config} should contain a [manifests] section with at least a 'folder' key.")
    
    if "urls" not in config.sections():
        raise ValueError
    
    if args.mode in ["local", "staging", "prod"] and args.mode not in config.urls:
        raise ValueError

    emojy, msg, color, log_lvl = interpret(True)
    logger.info("scenery set-up", style=color)
    
    return True

###################
# DJANGO CONFIG
###################

def django_setup(args: argparse.Namespace) -> bool:
    """Set up the Django environment.

    This function sets the DJANGO_SETTINGS_MODULE environment variable and calls django.setup().

    Args:
        settings_module (str): The import path to the Django settings module.
    """


    import django
    
    sys.path.append(os.path.join('.'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", args.django_settings_module)
    logger.debug(f"{os.environ.get('DJANGO_SETTINGS_MODULE')=}")

    django.setup()
    
    from django.conf import settings as django_settings
    logger.debug(f"{django_settings.INSTALLED_APPS=}")

    success = django_settings.configured

    emojy, msg, color, log_lvl = interpret(success)
    logger.log(log_lvl, "django set-up", style=color)
    
    return success


###################
# INTEGRATION TESTS
###################

def integration_tests(args: argparse.Namespace) -> bool:
    """
    Execute the main functionality of the scenery test runner.

    Returns:
        exit_code (int): Exit code indicating success (0) or failure (1)
    """

    report_data = run_integration_tests(args)

    success = True
    for filename, manifest_integration_tests_data in report_data.items():
        manifest_success = report_manifest_integration_test(manifest_integration_tests_data, filename)
        success &= manifest_success

    return success


def run_integration_tests(args: argparse.Namespace):

    # NOTE mad: this needs to be loaded afeter scenery_setup and django_setup
    from scenery.core import process_manifest_as_integration_test


    # FIXME mad: this is here to be able to load driver in two places
    # See also core.TestsLoader.tests_from_manifest.
    # Probably not a great pattern but let's fix this later
    # driver = get_selenium_driver(headless=args.headless)
    driver = None


    report_data = {}
    for filename in iter_on_manifests(args):

        # report_data[filename] = process_manifest_as_integration_test(filename, args=args, driver=driver)
        manifest_results = process_manifest_as_integration_test(filename, args=args, driver=driver)
        
        # Pivot report data to have one row per case x directive
        for mode, mode_results in manifest_results.items():
            if not mode_results:
                continue
            for test_name, test_result in mode_results.items():


                # Format test_name for nice display
                test_name = test_name.replace("scenery.core.", "")
                m = re.match(r"([^\.]+)\.([^\.]+\.[^\.]+).([^\.]+)", test_name)
                filename, mode, test_name = m.groups()


                m = re.match(r"test_case_(.+)_scene_([0-9]+)",test_name)
                case_name, scene_id = m.groups()


                test_name = f"{filename}.{scene_id}.{case_name}"

                report_data[filename] = report_data.get(filename, {})
                report_data[filename][test_name] = report_data[filename].get(test_name, {})

                report_data[filename][test_name][mode] = test_result


    return report_data


###################
# LOAD TESTS
###################

def load_tests(args: argparse.Namespace) -> bool:
    # NOTE mad: this needs to be loaded after scenery_setup and django_setup
    from scenery.core import process_manifest_as_load_test


    report_data = {}
    for filename in iter_on_manifests(args):   
        report_data[filename] = {}     
        results = process_manifest_as_load_test(filename, args=args)
        report_data[filename].update(results)

    success = True
    for filename, manifest_load_test_data in report_data.items():
        file_level_success = report_manifest_load_test(manifest_load_test_data)
        success &= file_level_success

    return success


###################
# CODE
###################

def inspect_code(args: argparse.Namespace) -> bool:
    from scenery.inspect_code import count_line_types

    report_data = {}

    # Get all files recursively
    folder = pathlib.Path(args.folder)

    # TODO: just the directory (make option)

    # All files
    for file_path in folder.rglob('*.py'):
        if file_path.is_file():
            report_data[str(file_path)] = count_line_types(file_path)

    success = report_inspect(report_data)

    return success

