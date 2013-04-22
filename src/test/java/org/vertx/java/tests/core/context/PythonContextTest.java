package org.vertx.java.tests.core.context;

import org.vertx.java.testframework.TestBase;

/**
 * @author <a href="https://github.com/sjhorn">Scott Horn</a>
 */
public class PythonContextTest extends TestBase {
    
  @Override
  protected void setUp() throws Exception {
    super.setUp();
    startApp("core/context/test_client.py");
  }

  @Override
  protected void tearDown() throws Exception {
    super.tearDown();
  }

  public void test_run_on_context() {
    startTest(getMethodName());
  }

  public void test_get_context() {
    startTest(getMethodName());
  }
        
}
