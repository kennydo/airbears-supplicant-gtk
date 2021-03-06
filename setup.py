from setuptools import setup

setup(name='airbears-supplicant-gtk',
      description='Supplicant to automatically log you into AirBears whenever you connect to AirBears',
      author='Kenny Do',
      author_email='kennydo@berkeley.edu',
      packages=['airbears_supplicant_gtk',
                 'airbears_supplicant_gtk.calnet',
                 'airbears_supplicant_gtk.ui'],
      package_data={
        'airbears_supplicant_gtk.ui': ['assets/*.png', 'assets/*.glade'],
      },
      entry_points={
        "gui_scripts": [
            "airbears_supplicant_gtk = airbears_supplicant_gtk.supplicant:main"
        ],
      },
      version='0.1.0',
      long_description="""
This supplicant is intended to run in the background on your laptop, so that
when you connect to the AirBears WiFi network, it will log you into CalNet if neccesary.
                       """,
      classifiers=['Programming Language :: Python',
                   'Topic :: System :: Networking'],
      )
