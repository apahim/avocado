# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; specifically version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#

import pickle
import tarfile
import os
import tempfile

from avocado.core import test
from avocado.core.loader import loader

if __name__ == '__channelexec__':
    os.sys.path.append(os.path.expanduser('~/avocado/tests'))
    tf = channel.receive()
    test_factory = pickle.loads(tf)
    content = channel.receive()

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as module_tmp:
        module_tmp.write(content)
    test_factory[1]['modulePath'] = module_tmp.name
    instance = loader.load_test(test_factory)
    module_tmp.delete

    early_state = instance.get_state()
    et = pickle.dumps(early_state, pickle.HIGHEST_PROTOCOL)
    channel.send(et)

    instance.run_avocado()

    state = instance.get_state()
    st = pickle.dumps(state, pickle.HIGHEST_PROTOCOL)
    channel.send(st)

    log_tmp = tempfile.NamedTemporaryFile(suffix=".tgz", delete=False)
    with tarfile.open(log_tmp.name, "w:gz") as tar:
        tar.add(instance.logdir, arcname=os.path.basename(instance.logdir))
    with open(log_tmp.name, 'r') as log_file:
        log = log_file.read()
    log_tmp.delete
    channel.send(log)
