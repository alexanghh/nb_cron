import setuptools
import versioneer

setuptools.setup(
    name="nb_cron",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/alexanghh/nb_cron",
    author="alexanghh",
    author_email="alexanghh@gmail.com",
    description="Manage your crontab from the Jupyter Notebook",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'notebook>=4.3.1',
        'croniter>=1.0.13',
        'python-crontab>=2.5.1'
    ]
)
