def deprecated(message):
  """
  Decorator for displaying a deprecation warning message via the Vert.x logger.

  Keyword arguments:
  @param message: The warning message to display.

  @return: A function wrapper that displays a deprecation warning when
  the function is called.
  """
  import org.vertx.java.platform.impl.JythonVerticleFactory
  log = org.vertx.java.platform.impl.JythonVerticleFactory.container.logger()
  def wrap(f):
    def deprecated_function(*args, **kwargs):
      log.warn(message)
      return f(*args, **kwargs)
    return deprecated_function
  return wrap
