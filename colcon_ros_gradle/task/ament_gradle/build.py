# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0

import os

from colcon_core.logging import colcon_logger

from colcon_gradle.task.gradle.build import GradleBuildTask

logger = colcon_logger.getChild(__name__)


class AmentGradleBuildTask(GradleBuildTask):

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--ament-gradle-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to Gradle projects. '
            'Arguments matching other options must be prefixed by a space,\n'
            'e.g. --ament-gradle-args " --help"')
        parser.add_argument(
            '--ament-gradle-task',
            help='Run a specific task instead of the default task')

    async def _build(self, args, env):
        ament_dependencies = ':'.join(
            [os.path.join(
                dep, 'share', pkg
            ) for pkg, dep in self.context.dependencies.items()])
        ament_exec_dependency_paths_in_workspace = ':'.join(
            [os.path.join(
                dep, 'share', pkg
            ) for pkg, dep in self.context.dependencies.items()
            if pkg in self.context.pkg.dependencies['run']])

        args.gradle_args = (args.gradle_args or [])
        args.gradle_args += ['-Pament.source_space={}'.format(args.path)]
        args.gradle_args += ['-Pament.build_space={}'.format(args.build_base)]
        args.gradle_args += ['-Pament.install_space={}'.format(args.install_base)]
        args.gradle_args += ['-Pament.dependencies={}'.format(ament_dependencies)]
        args.gradle_args += ['-Pament.package_manifest.name={}'.format(self.context.pkg.name)]
        args.gradle_args += ['-Pament.exec_dependency_paths_in_workspace={}'.format(
            ament_exec_dependency_paths_in_workspace)]
        # TODO(esteve): ament.gradle_recursive_dependencies is hardcoded to False for now
        args.gradle_args += ['-Pament.gradle_recursive_dependencies={}'.format(False)]
        return await super(AmentGradleBuildTask, self)._build(args, env)

    async def _install(self, args, env):
        self.progress('install')
