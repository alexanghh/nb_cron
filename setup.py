import setuptools
import versioneer

setuptools.setup(
    name="nb_cron",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/alexanghh/nb_cron",
    author="Continuum Analytics",
    description="Manage your crontab from the Jupyter Notebook",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False
)
