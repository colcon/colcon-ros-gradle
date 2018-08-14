# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0



from colcon_gradle.task.gradle.test import GradleTestTask
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint

logger = colcon_logger.getChild(__name__)


class RosGradleTestTask(TaskExtensionPoint):
    """Test ROS Gradle packages."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--ros-gradletest-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to Gradle projects. '
            'Arguments matching other options must be prefixed by a space,\n'
            'e.g. --gradletest-args " --help"')
        parser.add_argument(
            '--ros-gradle-task',
            help='Run a specific task instead of the default task')

    async def test(self, *, additional_hooks=None):  # noqa: D102
        logger.info(
            "Testing ROS package in '{args.path}' with build type "
            "'ros.gradle'".format_map(locals()))

        # reuse Gradle test task
        extension = GradleTestTask()
        extension.set_context(context=self.context)

        return await extension.test()
