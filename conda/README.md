# Building Humbug for Anaconda

This is currently a manual process. We will automate this if there is enough interest.

To release to your private conda channel:

1. Make sure you have `miniconda` installed: https://docs.conda.io/en/latest/miniconda.html

2. Make sure you have [anaconda-client](https://github.com/Anaconda-Platform/anaconda-client)
   installed and active on your `PATH`. Run `anaconda login` and log in with your Anaconda
   credentials.

3. Wipe all subdirectories of this directory: `rm -r ./*/`

4. Generate recursive `conda skeleton` for `humbug`: `~/miniconda3/bin/conda skeleton pypi humbug --recursive`.

5. Set conda to auto-upload builds: `~/miniconda3/bin/conda config --set anaconda_upload yes`

6. Build and upload: `~/miniconda3/bin/conda build humbug`

The builds end up here: https://anaconda.org/bugout.dev/humbug

Good luck and may the giant snakes smile upon you.
