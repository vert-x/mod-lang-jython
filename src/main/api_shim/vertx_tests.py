import vertx
from org.vertx.testtools import VertxAssert
from org.vertx.java.platform.impl import JythonVerticleFactory

VertxAssert.initialize(JythonVerticleFactory.vertx)

def start_tests(locs) :
    method_name = vertx.config()['methodName']
    locs[method_name]()