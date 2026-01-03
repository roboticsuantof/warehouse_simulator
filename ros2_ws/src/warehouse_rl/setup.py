from setuptools import setup

package_name = 'warehouse_rl'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kishouandrea',
    maintainer_email='tu_email@todo.todo',
    description='Paquete de RL para LACORO',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'entrenar = warehouse_rl.train_rl:train',
            'evaluar = warehouse_rl.run_policy:run_evaluation',
        ],
    },
)