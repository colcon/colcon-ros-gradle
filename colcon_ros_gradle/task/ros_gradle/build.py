# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0

from colcon_core.logging import colcon_logger

from colcon_gradle.task.gradle import GradleBuildTask

logger = colcon_logger.getChild(__name__)


class RosGradleBuildTask(GradleBuildTask):

    async def _install(self, args, env):
        self.progress('install')
