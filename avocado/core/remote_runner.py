

import execnet
import pickle
import os

import remote_test
from .runner import TestRunner
from ..utils import archive


class RemoteTestRunner(TestRunner):

    def __init__(self, job, test_result):
        super(RemoteTestRunner, self).__init__(job, test_result)

    def _run_test(self, test_factory, queue):
        hostname = getattr(self.job.args, 'remote_hostname', None)
        username = getattr(self.job.args, 'remote_username', None)
        test_factory[1]['job'] = None
        conn = 'ssh=%s@%s' % (username, hostname)
        gw = execnet.makegateway(conn)
        channel = gw.remote_exec(remote_test)

        tf = pickle.dumps(test_factory,pickle.HIGHEST_PROTOCOL)
        channel.send(tf)

        with open(test_factory[1]['modulePath'], 'r') as f:
            content = f.read()
        channel.send(content)

        et = channel.receive()
        early_state = pickle.loads(et)

        self.result.start_test(early_state)
        early_state['early_status'] = True
        queue.put(early_state)

        st = channel.receive()
        state = pickle.loads(st)
        queue.put(state)

        content = channel.receive()
        with open('/tmp/log.tgz', 'w') as f:
            f.write(content)

        archive.uncompress('/tmp/log.tgz', os.path.join(self.job.logdir, 'test-results'))
