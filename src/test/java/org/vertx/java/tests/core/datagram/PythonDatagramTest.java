package org.vertx.java.tests.core.datagram;

import org.junit.Test;
import org.vertx.java.core.logging.Logger;
import org.vertx.java.core.logging.impl.LoggerFactory;
import org.vertx.java.testframework.TestBase;

/**
 * @author <a href="https://github.com/sjhorn">Scott Horn</a>
 */
public class PythonDatagramTest extends TestBase {

  private static final Logger log = LoggerFactory.getLogger(PythonDatagramTest.class);

  @Override
  protected void setUp() throws Exception {
    super.setUp();
    startApp("core/datagram/test_client.py");
  }

  @Override
  protected void tearDown() throws Exception {
    super.tearDown();
  }

  @Test
  public void test_send_receive() throws Exception {
    startTest(getMethodName());
  }

  @Test
  public void test_listen_host_port() throws Exception {
    startTest(getMethodName());
  }

  @Test
  public void test_listen_port() throws Exception {
    startTest(getMethodName());
  }

  @Test
  public void test_listen_port_multiple_times() throws Exception {
    startTest(getMethodName());
  }

  @Test
  public void test_echo() throws Exception {
    startTest(getMethodName());
  }

  @Test
  public void test_send_after_close_fails() throws Exception {
    startTest(getMethodName());
  }

  @Test
  public void test_broadcast() throws Exception {
    startTest(getMethodName());
  }

  @Test
  public void test_configure() throws Exception {
    startTest(getMethodName());
  }
}
