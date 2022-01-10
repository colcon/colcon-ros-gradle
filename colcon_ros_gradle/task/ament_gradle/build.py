# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0

import os
from pathlib import Path

from colcon_core.logging import colcon_logger
from colcon_core.shell import create_environment_hook
from colcon_gradle.task.gradle.build import GradleBuildTask

logger = colcon_logger.getChild(__name__)


class AmentGradleBuildTask(GradleBuildTask):
    """Build ament_gradle packages."""

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

    async def build(  # noqa: D102
        self, *, additional_hooks=[], skip_hook_creation=False
    ):
        pkg = self.context.pkg
        args = self.context.args

        additional_hooks += create_environment_hook(
            'ament_prefix_path', Path(args.install_base), pkg.name,
            'AMENT_PREFIX_PATH', args.install_base,
            mode='prepend')

        return await super(AmentGradleBuildTask, self).build(
            additional_hooks=additional_hooks,
            skip_hook_creation=skip_hook_creation
        )

    async def _build(self, args, env):
        ament_dependencies = ':'.join([
            os.path.join(dep, 'share', pkg)
            for pkg, dep in self.context.dependencies.items()
        ])
        ament_exec_dependency_paths_in_workspace = ':'.join([
            os.path.join(dep, 'share', pkg)
            for pkg, dep in self.context.dependencies.items()
            if pkg in self.context.pkg.dependencies['run']
        ])

        args.gradle_args = (args.gradle_args or [])
        args.gradle_args.append(f'-Pament.source_space={args.path}')
        args.gradle_args.append(f'-Pament.build_space={args.build_base}')
        args.gradle_args.append(f'-Pament.install_space={args.install_base}')
        args.gradle_args.append(f'-Pament.dependencies={ament_dependencies}')
        args.gradle_args.append(
            f'-Pament.package_manifest.name={self.context.pkg.name}'
        )
        args.gradle_args.append(
            '-Pament.exec_dependency_paths_in_workspace='
            f'{ament_exec_dependency_paths_in_workspace}'
        )
        # TODO(esteve): ament.gradle_recursive_dependencies is hard-coded to
        #               False for now
        args.gradle_args.append('-Pament.gradle_recursive_dependencies=False')
        return await super(AmentGradleBuildTask, self)._build(args, env)

    async def _install(self, args, env):
        self.progress('install')

        # Create Marker file
        package_name = self.context.pkg.name
        install_base = args.install_base
        resource_index_dir = os.path.join(
            'share', 'ament_index', 'resource_index', 'packages'
        )

        marker_file_path = Path(
            os.path.join(install_base, resource_index_dir, package_name)
        )
        marker_file_path.parent.mkdir(parents=True, exist_ok=True)
        marker_file_path.touch()
