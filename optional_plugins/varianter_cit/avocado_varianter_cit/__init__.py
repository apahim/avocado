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

import ConfigParser
import hashlib
import itertools
import os
import sys

from six import iteritems

from avocado.core import exit_codes
from avocado.core.output import LOG_UI
from avocado.core.plugin_interfaces import CLI
from avocado.core.plugin_interfaces import Varianter
from avocado.core.tree import TreeNode
from avocado.core.varianter import AvocadoParams
from avocado.utils import path as utils_path
from avocado.utils import process


class VarianterCitCLI(CLI):

    """
    CIT Varianter options
    """

    name = 'cit'
    description = "CIT Varianter options for the 'run' subcommand"

    def configure(self, parser):

        for name in ("run", "variants"):  # intentionally ommiting "multiplex"
            subparser = parser.subcommands.choices.get(name, None)
            if subparser is None:
                continue
            cit = subparser.add_argument_group('CIT varianter options')
            cit.add_argument('--cit-parameter-file', metavar='PATH',
                             help=("Paths to a parameter file"))
            cit.add_argument('--cit-parameter-path', metavar='PATH',
                             default='/run',
                             help=('Default path for parameters generated '
                                   'on the CIT variants'))
            cit.add_argument('--cit-order-of-combinations',
                             metavar='ORDER', type=int, default=2,
                             help=("Order of combinations. Defaults to "
                                   "%(default)s, maximum number is specific "
                                   "to parameter file content"))

    def run(self, args):
        pass


class VarianterCit(Varianter):

    """
    Processes the parameters file into variants
    """

    name = 'cit'
    description = "CIT Varianter"

    def initialize(self, args):
        self.variants = None
        error = False

        cit_parameter_file = getattr(args, "cit_parameter_file", None)
        if cit_parameter_file is None:
            return
        else:
            cit_parameter_file = os.path.expanduser(cit_parameter_file)
            if not os.access(cit_parameter_file, os.R_OK):
                LOG_UI.error("parameter file '%s' could not be found or "
                             "is not readable", cit_parameter_file)
                error = True

        if error:
            if args.subcommand == 'run':
                sys.exit(exit_codes.AVOCADO_JOB_FAIL)
            else:
                sys.exit(exit_codes.AVOCADO_FAIL)

        self.parameter_path = getattr(args, "cit_parameter_path")

        config = ConfigParser.ConfigParser()
        config.read(cit_parameter_file)

        parameters = [(key, value.split(', '))
                      for key, value in config.items('parameters')]
        constraints = [(key, value.split(', '))
                       for key, value in config.items('constraints')]
        cit = Cit(parameters, constraints)
        self.headers, self.variants = cit.combine()

    def __iter__(self):
        if self.variants is None:
            return

        variant_ids = []
        for variant in self.variants:
            base_id = "-".join([variant.get(key) for key in self.headers])
            variant_ids.append(base_id + '-' +
                               hashlib.sha1(base_id).hexdigest()[:4])

        for vid, variant in itertools.izip(variant_ids, self.variants):
            variant_tree_nodes = []
            for key, val in variant.items():
                variant_tree_nodes.append(TreeNode(key, {key: val}))

            yield {"variant_id": vid,
                   "variant": variant_tree_nodes,
                   "mux_path": self.parameter_path}

    def __len__(self):
        return sum(1 for _ in self)

    def update_defaults(self, defaults):
        pass

    def to_str(self, summary, variants, **kwargs):
        """
        Return human readable representation

        The summary/variants accepts verbosity where 0 means silent and
        maximum is up to the plugin.

        :param summary: How verbose summary to output (int)
        :param variants: How verbose list of variants to output (int)
        :param kwargs: Other free-form arguments
        :rtype: str
        """
        out = []
        if variants:
            out.append("CIT Variants (%i):" % len(self))
            for variant in self:
                out.append('Variant %s:    %s' % (variant["variant_id"],
                                                  self.parameter_path))

                if variants > 1:
                    for node in variant["variant"]:
                        for key, value in iteritems(node.environment):
                            out.append("    %s:%s => %s" % (self.parameter_path,
                                                            key,
                                                            value))

        return "\n".join(out)


class Cit(object):
    def __init__(self, parameters, constraints):
        self.parameters = parameters
        # Constraints are not implemented in this example
        self.constraints = constraints

    def combine(self):
        """
        Example of method to combine the parameters. Will be
        replaced by the actual CIT algorithm.

        Returns a tuple: (headers, combinations)
            headers: list of parameters keys.
            combinations: list of dictionaries. Each dictionary
                          represents a combination of parameters.

        Example:
            p1: x1, x1
            p2: y1, y2

            return (['p1', 'p2'],
                    [{'p1': 'x1', 'p2': 'y1'},
                     {'p1': 'x1', 'p2': 'y2'},
                     {'p1': 'x2', 'p2': 'y1'},
                     {'p1': 'x2', 'p2': 'y2'}])
        """
        combinations = []
        headers = [item[0] for item in self.parameters]
        for combination in itertools.product(*(params[1]
                                               for params in self.parameters)):
            combinations.append(dict(zip(headers, combination)))
        return headers, combinations
