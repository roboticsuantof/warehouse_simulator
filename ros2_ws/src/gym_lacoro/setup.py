from setuptools import find_packages, setup

package_name = 'gym_lacoro'

data_files = list()

data_files.append(
    ('share/ament_index/resource_index/packages',
     ['resource/' + package_name]))

data_files.append(('share/' + package_name, ['package.xml']))

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Angel Ayala',
    maintainer_email='aaam@ecomp.poli.br',
    description='Gym environment for the Warehouse competition at LACORO 2025.',
    license='GPL-3.0-only',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
