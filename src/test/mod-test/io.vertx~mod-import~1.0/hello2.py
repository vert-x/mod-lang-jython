from test_utils import TestUtils
tu = TestUtils()

class NetTest(object):

    def test_import_module(self):
        print "in test_import_module"
        tu.test_complete()


tu.register_all(NetTest())
tu.app_ready()

print "in hello2"

