# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0


import copy

from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_core.plugin_system import satisfies_version
from colcon_gradle.package_identification.gradle \
    import GradlePackageIdentification
from colcon_ros.package_identification.ros \
    import RosPackageIdentification

class RosGradlePackageIdentification(PackageIdentificationExtensionPoint):
    """
    Identify ROS Gradle packages with `package.xml` and `build.gradle` files.
    """

    # the priority needs to be higher than the ROS extensions identifying
    # packages using the build systems supported by ROS Gradle.
    PRIORITY = 160

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, desc):  # noqa: D102
        if desc.type is not None and desc.type != 'ros.gradle':
            return

        # Preserving the state of the package descriptor so as not to overload
        # the build type is a "common", one like "cmake".
        tmp_desc = copy.deepcopy(desc)

        # Call ROS package identification extention.
        ros_extension = RosPackageIdentification()
        ros_extension.identify(tmp_desc)

        # Validate that is ROS gradle package.
        if tmp_desc.type != 'ros.gradle':
            return

        # Disable ROS Gradle build type for use Gradle package identification
        # extension (reject if build type has defined).
        tmp_desc.type = None

        # Call Gradle package identification extention
        # (for append gradle logic).
        gradle_extention = GradlePackageIdentification()
        gradle_extention.identify(tmp_desc)
        
        # Validate that is gradle package logic.
        if tmp_desc.type != 'gradle':
            return

        # Update package descriptor instance (if has valide build type).
        desc.type = 'ros.gradle'
        desc.name = tmp_desc.name
        desc.dependencies = tmp_desc.dependencies
        desc.hooks = tmp_desc.hooks
        desc.metadata = tmp_desc.metadata

