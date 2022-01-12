# colcon-ros-gradle

[![Run tests](https://github.com/colcon/colcon-ros-gradle/actions/workflows/ci.yaml/badge.svg)](https://github.com/colcon/colcon-ros-gradle/actions/workflows/ci.yaml)

An extension for [colcon-core](https://github.com/colcon/colcon-core) to support [ROS 2 Gradle](https://plugins.gradle.org/plugin/org.ros2.tools.gradle) projects.

## Try it out

### Using pip

```
pip install -U colcon-ros-gradle
```

### From source

Follow the instructions at https://colcon.readthedocs.io/en/released/developer/bootstrap.html, except in "Fetch the sources" add the following to `colcon.repos`:

```yaml
  colcon-ros-gradle:
    type: git
    url: https://github.com/colcon/colcon-ros-gradle.git
    version: main
```

After that, run the `local_setup` file, build any colcon workspace with Gradle projects in it, and report any issues!
