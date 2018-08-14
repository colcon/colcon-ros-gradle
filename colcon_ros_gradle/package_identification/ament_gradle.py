# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0

import os
from pathlib import Path
import re

from colcon_core.package_identification import logger
from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_core.plugin_system import satisfies_version


class AmentGradlePackageIdentification(PackageIdentificationExtensionPoint):
    """Identify Gradle packages with `build.gradle` and `package.xml` files."""

    PRIORITY = 160

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, metadata):  # noqa: D102
        if metadata.type is not None and metadata.type != 'ament_gradle':
            return

        build_gradle = metadata.path / 'build.gradle'
        if not build_gradle.is_file():
            return

        package_xml = metadata.path / 'package.xml'
        if not package_xml.is_file():
            return

        data = extract_data(build_gradle)
        if not data['name'] and not metadata.name:
            raise RuntimeError(
                "Failed to extract project name from '%s'" % build_gradle)

        if metadata.name is not None and metadata.name != data['name']:
            raise RuntimeError('Package name already set to different value')

        metadata.type = 'ament_gradle'
        if metadata.name is None:
            metadata.name = data['name']
        metadata.dependencies['build'] |= data['depends']
        metadata.dependencies['run']   |= data['depends']
        metadata.dependencies['test']  |= data['depends']

def extract_data(build_gradle):
    """
    Extract the project name and dependencies from a build.gradle file.

    :param Path build_gradle: The path of the build.gradle file
    :rtype: dict
    """
    # Content for dependencies
    content_build_gradle = super(AmentGradlePackageIdentification, self).extract_content(build_gradle)
    match = re.search(r'apply plugin: ("|\')org.ros2.tools.gradle\1', content)
    if not match:
        raise RuntimeError("Gradle plugin missing, please add the following to build.gradle: \"apply plugin: 'org.ros2.tools.gradle'\"")

    # Content for name
    content_setting_gradle = extract_content(build_gradle.parent, 'settings.gradle')

    data = {}
    data['name'] = extract_project_name(content_setting_gradle)
    # fallback to the directory name
    if data['name'] is None:
        data['name'] = build_gradle.parent.name

    # extract dependencies from all Gradle files in the project directory
    data['depends'] = set()

    return data