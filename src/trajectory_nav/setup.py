from setuptools import find_packages, setup

package_name = 'trajectory_nav'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy', 'scipy', 'matplotlib'],
    zip_safe=True,
    maintainer='hppmp',
    maintainer_email='pavanmp1402@gmail.com',
    description='Trajectory navigation package with waypoint loading and spline smoothing',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'waypoint_loader=trajectory_nav.waypoint_loader:main',
            'spline_smoother=trajectory_nav.spline_smoother:main',
        ],
    },
)
