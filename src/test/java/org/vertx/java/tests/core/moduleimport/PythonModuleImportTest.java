package org.vertx.java.tests.core.moduleimport;

import org.vertx.java.testframework.TestBase;

/**
 * @author <a href="https://github.com/sjhorn">Scott Horn</a>
 */
public class PythonModuleImportTest extends TestBase {

  @Override
  protected void setUp() throws Exception {
    super.setUp();
    startMod("io.vertx~mod-import~1.0");
  }

  @Override
  protected void tearDown() throws Exception {
    super.tearDown();
  }

  public void test_import_module() {
    startTest(getMethodName());
  }


}
