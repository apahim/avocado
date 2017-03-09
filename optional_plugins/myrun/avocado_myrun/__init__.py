import logging
import sys

from avocado.core import exit_codes
from avocado.core import job
from avocado.core.dispatcher import ResultDispatcher
from avocado.utils.data_structures import time_to_seconds
from avocado.plugins.yaml_to_mux import YamlToMux
from avocado.plugins.run import Run


class Run(Run):

    name = 'run'
    description = 'Hackish run'

    def run(self, args):
        """
        Run test modules or simple tests.

        :param args: Command line args received from the run subparser.
        """
        log = logging.getLogger("avocado.app")
        if args.unique_job_id is not None:
            try:
                int(args.unique_job_id, 16)
                if len(args.unique_job_id) != 40:
                    raise ValueError
            except ValueError:
                log.error('Unique Job ID needs to be a 40 digit hex number')
                sys.exit(exit_codes.AVOCADO_FAIL)
        try:
            args.job_timeout = time_to_seconds(args.job_timeout)
        except ValueError as e:
            log.error(e.message)
            sys.exit(exit_codes.AVOCADO_FAIL)

        log.info("xxx hacking around xxx")
        job_instance = job.Job(args)
        job_run = job_instance.run()
        result_dispatcher = ResultDispatcher()
        if result_dispatcher.extensions:
            result_dispatcher.map_method('render',
                                         job_instance.result,
                                         job_instance)
        return job_run
