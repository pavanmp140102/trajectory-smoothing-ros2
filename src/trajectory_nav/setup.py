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
        ('share/' + package_name + '/launch', ['launch/trajectory_nav.launch.py']),
        ('share/' + package_name + '/config', [
            'config/spline_smoother.yaml',
            'config/trajectory_generator.yaml',
            'config/pure_pursuit_controller.yaml',
        ]),
    ],
    install_requires=['setuptools', 'numpy', 'scipy', 'matplotlib', 'tf-transformations'],
    zip_safe=True,
    maintainer='hppmp',
    maintainer_email='pavanmp1402@gmail.com',
    description='Trajectory navigation package with waypoint loading, spline smoothing, and pure pursuit control',
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
            'trajectory_generator=trajectory_nav.trajectory_generator:main',
            'pure_pursuit_controller=trajectory_nav.pure_pursuit_controller:main',
            'trajectory_visualizer=trajectory_nav.trajectory_visualizer:main',
        ],
    },
)
