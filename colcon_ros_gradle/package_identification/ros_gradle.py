# Copyright 2018 Esteve Fernandez
# Licensed under the Apache License, Version 2.0

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

    PRIORITY = 160

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, desc):  # noqa: D102
        if desc.type is not None and desc.type != 'ros.gradle':
            return

        # Call ROS package identification extention.
        ros_extension = RosPackageIdentification()
        ros_extension.identify(desc)
        if desc.type != 'ros.gradle':
            return

        # Disable build type.
        desc.type = None

        # Call Gradle package identification extention.
        gradle_extention = GradlePackageIdentification()
        gradle_extention.identify(desc)
        if desc.type != 'gradle':
            return

        # Define build type (ros.gradle).
        desc.type = 'ros.gradle'

