package org.vertx.java.tests.core.sockjs;

import org.vertx.java.testframework.TestBase;

/**
 * @author <a href="https://github.com/kuujo">Jordan Halterman</a>
 */
public class PythonSockJSTest extends TestBase {

  @Override
  protected void setUp() throws Exception {
    super.setUp();
    startApp("core/sockjs/test_client.py");
  }

  @Override
  protected void tearDown() throws Exception {
    super.tearDown();
  }

  public void test_socket_created_hook() {
    startTest(getMethodName());
  }

  public void test_socket_closed_hook() {
    startTest(getMethodName());
  }

  public void test_send_or_pub_hook() {
    startTest(getMethodName());
  }

  public void test_pre_register_hook() {
    startTest(getMethodName());
  }

  public void test_post_register_hook() {
    startTest(getMethodName());
  }

  public void test_unregister_hook() {
    startTest(getMethodName());
  }

  public void test_authorise_hook() {
    startTest(getMethodName());
  }

}
