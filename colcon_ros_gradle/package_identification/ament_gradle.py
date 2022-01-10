# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0

import re

from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_core.plugin_system import satisfies_version
from colcon_gradle.package_identification.gradle import extract_content
from colcon_gradle.package_identification.gradle import extract_data
from colcon_gradle.package_identification.gradle \
    import GradlePackageIdentification
from colcon_ros.package_identification.ros import _get_package


class AmentGradlePackageIdentification(GradlePackageIdentification):
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

        gradle_data = gradle_extract_data(build_gradle)
        if not gradle_data['name'] and not metadata.name:
            raise RuntimeError(
                "Failed to extract project name from '%s'" % build_gradle)

        if metadata.name is not None and metadata.name != gradle_data['name']:
            raise RuntimeError('Package name already set to different value')

        metadata.type = 'ament_gradle'
        if metadata.name is None:
            metadata.name = gradle_data['name']

        ros_data = ros_extract_data(str(metadata.path))
        metadata.dependencies['build'] |= ros_data['build_depends']
        metadata.dependencies['run'] |= ros_data['run_depends']
        metadata.dependencies['test'] |= ros_data['test_depends']


def gradle_extract_data(build_gradle):
    """
    Extract the project name and dependencies from a build.gradle file.

    :param Path build_gradle: The path of the build.gradle file
    :rtype: dict
    """
    # Content for dependencies
    content_build_gradle = extract_content(build_gradle)
    match = re.search(
        r'apply plugin: ("|\')org.ros2.tools.gradle\1', content_build_gradle
    )
    if not match:
        raise RuntimeError(
            'Gradle plugin missing, please add the following to build.gradle:'
            " \"apply plugin: 'org.ros2.tools.gradle'\""
        )

    return extract_data(build_gradle)


def ros_extract_data(package_path):  # noqa: D103
    pkg = _get_package(str(package_path))

    depends = {}
    depends['build_depends'] = {dep.name for dep in pkg.build_depends}
    depends['run_depends'] = {dep.name for dep in pkg.run_depends}
    depends['test_depends'] = {dep.name for dep in pkg.test_depends}
    return depends
