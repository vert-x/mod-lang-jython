from test_utils import TestUtils
tu = TestUtils()

import hello2

print "in hello"

def vertx_stop():
    tu.unregister_all()
    tu.app_stopped()


