import anvil.server
import pytest
from ..DataAccess import ReportingDAModule
from ..Entities.Label import Label
from ..Entities.TestModule import TestModule
from .. import SystemProcess as sys

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestReportingDAModule(TestModule):
