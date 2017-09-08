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

"""
Avocado Plugin to create N-Wise Combinatorial Variants
"""


from avocado.core.plugin_interfaces import CLI


class CombinatorialCLI(CLI):

    """
    Enable/Configure Combinatorial generation of Variants
    """

    name = 'combinatorial'
    description = "Combinatorial options for 'run' subcommand"

    def configure(self, parser):
        run_subcommand_parser = parser.subcommands.choices.get('run', None)
        if run_subcommand_parser is None:
            return

        msg = 'combinatorial options'
        parser = run_subcommand_parser.add_argument_group(msg)
        parser.add_argument('--combinatorial',
                            dest='combinatorial', default=None,
                            help='Specify the number of combined elements')
        self.configured = True

    def run(self, args):
        pass
