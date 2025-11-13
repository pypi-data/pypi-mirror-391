"""General functions and classes used by other modules."""

import argparse
import enum
import os
import unittest
import requests
from types import TracebackType
from typing import Any, Iterable, List, TypeVar, Union

from scenery import config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import yaml



###################
# TYPES
###################

# NOTE mad: this is here to prevent circular import and still use those types
# either to check isinstance(x, cls) (see reponse_checker for instance),
# and type checking



class RemoteBackendTestCase(unittest.TestCase):
    """A TestCase for backend testing on a remote server."""
    mode: str
    session: requests.Session
    base_url: str
    headers: dict[str, str]

class RemoteFrontendTestCase(unittest.TestCase):
    """A TestCase for backend testing on a remote server."""
    mode: str
    driver: webdriver.Chrome
    # session: requests.Session
    base_url: str
    headers: dict[str, str]

class LoadTestCase(unittest.TestCase):
    """A TestCase for load testing on a remote server."""
    mode: str
    session: requests.Session
    headers: dict[str, str]
    base_url: str
    data: dict[str, List[dict[str, int|float]]]
    users:int
    requests_per_user:int


# NOTE mad: proper implementation is in django utils
class DjangoBackendTestCase:
    def __init__(self, *args, **kwargs):
            ImportError("django required")

class DjangoFrontendTestCase:
    def __init__(self, *args, **kwargs):
            ImportError("django required")


class Framework(enum.Enum):
    DJANGO = "django"


SceneryTestCaseTypes = Union[RemoteBackendTestCase, RemoteFrontendTestCase, LoadTestCase]

SceneryTestCase = TypeVar("SceneryTestCase", bound=SceneryTestCaseTypes)



###################
# SELENIUM
###################


def get_selenium_driver(headless: bool, page_load_timeout: int = 30) -> webdriver.Chrome:
    """Return a Selenium WebDriver instance configured for Chrome.

    Args:
        headless (bool): Whether to run Chrome in headless mode.
        page_load_timeout (int): Maximum time in seconds to wait for the page to load.
            If the timeout is exceeded, a TimeoutException will be thrown.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--window-size=1920,1080')
    # chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    # Essential for running in a containerized environment
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Optional: reduce resource usage
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')

    # NOTE mad: used to wait until domcontent loaded
    # see: https://www.selenium.dev/documentation/webdriver/drivers/options/
    chrome_options.page_load_strategy = 'eager' 
    if headless:
        chrome_options.add_argument("--headless=new")         # NOTE mad: For newer Chrome versions
        # chrome_options.add_argument("--headless")           
    driver = webdriver.Chrome(options=chrome_options)  #  service=service
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(page_load_timeout)  # Set timeout for page load
    return driver



# def get_selenium_driver():
#     """Configure Chrome for Scalingo environment"""
#     chrome_options = Options()
    
#     # Essential for running in a containerized environment
#     chrome_options.add_argument('--headless')
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--disable-dev-shm-usage')
#     chrome_options.add_argument('--disable-gpu')
    
#     # Optional: reduce resource usage
#     chrome_options.add_argument('--disable-extensions')
#     chrome_options.add_argument('--disable-logging')
#     chrome_options.add_argument('--log-level=3')
    
#     # The buildpack sets up chromedriver automatically
#     driver = webdriver.Chrome(options=chrome_options)
    
#     return driver

########
# YAML #
########


def read_yaml(filename: str) -> Any:
    """Read and parse a YAML file.

    Args:
        filename (str): The path to the YAML file to be read.

    Returns:
        Any: The parsed content of the YAML file.

    Raises:
        yaml.YAMLError: If there's an error parsing the YAML file.
        IOError: If there's an error reading the file.
    """
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def iter_on_manifests(args: argparse.Namespace) -> Iterable[str]:
    for filename in os.listdir(config.manifests_folder):
        if args.manifest is not None and filename.replace(".yml", "") != args.manifest:
            continue

        yield filename



##################
# UNITTEST
##################

class CustomTestResult(unittest.TestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_tests = []
        self.successes = []
    
    def startTest(self, test):
        super().startTest(test)
        self.all_tests.append(test)
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)

    def addError(
        self,
        test: unittest.TestCase,
        err: (tuple[type[BaseException], BaseException, TracebackType] | tuple[None, None, None]),
    ) -> None:
        super().addError(test, err)
        self.caught_exception = err


    def as_dict(self):

        d = {}

        for test, traceback in self.errors:
            d[test.id()] = {
                "passed": False,
                "status": "error",
                "traceback": traceback
            }
            

        for test, traceback in self.failures:
            d[test.id()]  = {
                "passed": False,
                "status": "failure",
                "traceback": traceback
            }
            
        for test in self.successes:
            d[test.id()] = {
                "passed": True,
                "status": "sucess",
                "traceback": None
            }
        
        return d




