# construction how to bundle and publish that package

from setuptools import setup, find_packages

setup(
    name = 'hello-thang1062005',
    version = '0.2',
    packages = find_packages(),
    install_requires = [
        # add dependencies
        # eg: ' numpy >= ..'
    ],
    # cli
    entry_points = {
        'console_scripts': [
            'gayhello = hello:hello',
        ],
    },
)

# sdist: source distribution
# phân phối mã nguồn, bên trong có toàn bộ mã nguồn (folder)
# bdist_wheel: built distribution
# tệp .whl, các tệp đã được build sẵn sàng để chạy
