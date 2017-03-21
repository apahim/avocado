# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: Red Hat Inc. 2017
# Authors: Amador Pahim <apahim@redhat.com>

import collections
import subprocess

from avocado.core import exceptions
from avocado.core import loader
from avocado.core import output
from avocado.core import test
from avocado.core.plugin_interfaces import CLI
from avocado.core.runner import TestRunner
from avocado.utils import path as utils_path
from robot.parsing.model import TestData


ROBOT_BINARY_NAME = 'robot'


class RobotTest(test.SimpleTest):

    """
    Run a Robot command as a SIMPLE test.
    """

    def __init__(self,
                 name,
                 params=None,
                 base_logdir=None,
                 job=None,
                 external_runner=None):
        super(RobotTest, self).__init__(name, params, base_logdir, job)

    @property
    def filename(self):
        """
        Returns the path of the robot test suite.
        """
        return self.name.name.split(':')[0]

    def test(self):
        """
        Create the Robot command and execute it.
        """
        try:
            robot_binary = utils_path.find_command(ROBOT_BINARY_NAME)
        except utils_path.CmdNotFoundError:
            raise exceptions.TestError('"%s" binary not found.' %
                                       ROBOT_BINARY_NAME)

        suite_name, test_name = self.name.name.split(':')[1].split('.')
        cmd = '%s --suite "%s" --test "%s" %s' % (robot_binary,
                                                  suite_name,
                                                  test_name,
                                                  self.filename)
        self._command = cmd
        self.execute_cmd()


class RobotLoader(loader.TestLoader):
    """
    Robot loader class
    """
    name = "robot"

    def __init__(self, args, extra_params):
        super(RobotLoader, self).__init__(args, extra_params)

    def discover(self, url, which_tests=False):
        avocado_suite = []
        robot_suite = self._find_tests(TestData(parent=None, source=url))
        for item in robot_suite:
            for robot_test in robot_suite[item]:
                test_name = "%s:%s.%s" % (url, item, robot_test)
                avocado_suite.append((RobotTest, {'name': test_name}))
        return avocado_suite

    def _find_tests(self, data, test_suite={}):
        test_suite[data.name] = []
        for test in data.testcase_table:
            test_suite[data.name].append(test.name)
        for child_data in data.children:
            self._find_tests(child_data, test_suite)
        return test_suite

    @staticmethod
    def get_type_label_mapping():
        return {}

    @staticmethod
    def get_decorator_mapping():
        return {}


class RobotCLI(CLI):

    """
    Run Robot Framework tests
    """

    name = 'robot'
    description = "Robot Framework options for 'run' subcommand"

    def configure(self, parser):
        run_subcommand_parser = parser.subcommands.choices.get('run', None)
        if run_subcommand_parser is None:
            return

        msg = 'robot framework options'
        self.remote_parser = run_subcommand_parser.add_argument_group(msg)
        self.remote_parser.add_argument('--robot', action='store_true',
                                        default=False,
                                        help='Specify the robot test suite'
                                        ' directory')
        self.configured = True

    def run(self, args):
        if getattr(args, 'robot', None):
            loader.loader.clear_plugins()
            loader.loader.register_plugin(RobotLoader)
