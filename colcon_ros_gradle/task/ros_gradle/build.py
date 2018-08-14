# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0


from colcon_gradle.task.gradle.build import GradleBuildTask
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint

logger = colcon_logger.getChild(__name__)


class RosGradleBuildTask(TaskExtensionPoint):
    """Build ROS gradle packages."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--ros-gradle-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to Gradle projects. '
            'Arguments matching other options must be prefixed by a space,\n'
            'e.g. --ros-gradle-args " --help"')
        parser.add_argument(
            '--ros-gradle-task',
            help='Run a specific task instead of the default task')

    async def build(
        self, *, additional_hooks=None, skip_hook_creation=False
    ):  # noqa: D102
        args = self.context.args
        logger.info(
            "Building ROS package in '{args.path}' with build type 'ros.gradle'"
            .format_map(locals()))

        # reuse Gradle build task with additional logic.
        extension = GradleBuildTask()

        # Generate list of dependencies.
        deps = []
        for dep in self.context.pkg.dependencies['build'] or []:
            if dep in self.context.dependencies:
                deps.append(self.context.dependencies[dep])

        # Append extra arguments.
        ros_gradle_args = [
            '-Pcolcon.source_space=' + args.path,
            '-Pcolcon.build_space=' + args.build_base,
            '-Pcolcon.install_space=' + args.install_base,
            '-Pcolcon.dependencies=' + ':'.join(deps),
        ]
        args.gradle_args += ros_gradle_args

        extension.set_context(context=self.context)

        return await extension.build()

