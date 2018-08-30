# Wrapper over the Maxmind geoip2 library

This is a python 3 wrapper around Maxmind's geoip2 library (currently only supports City).
It automatically updates the database periodically.

You must have a Maxmind license for this to work.

There are two ways to use this library:

1. Directly fetch from Maxmind.  In this case you need to pass your license information in by either
    - setting the environment variable `MAXMIND_LICENSE_KEY`, or 
    - passing the argument `maxmind_license_key` to the Reader constructor (see Usage below).

2. Fetch from a cache that you maintain in S3.  In that case you need to pass the following arguments to the
constructor:
```
s3_bucket
s3_key  (defaults to GeoIP2-City.mmdb)
aws_access_key_id
aws_secret_access_key
```

If you are maintaing your own cache then you might want to look at this repo
https://github.com/ActivisionGameScience/maxmind-s3-fetcher

See below for Usage details.


## Quickstart for Conda users in Linux

Using the `conda` package manager is the quickest way to get going
without building anything:
```
# bootstrap the conda system
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
/bin/bash Miniconda3-latest-Linux-x86_64.sh

# point to our conda channel
echo "channels:\n  - ActivisionGameScience\n  - defaults" > ~/.condarc

# create and activate an environment
conda create -n py36 python=3.6 maxmind-wrapper ipython -y
source activate py36

# start ipython and you're cooking!
```

## Usage

The API is just a simple wrapper around `geoip2`.
```
    from maxmind_wrapper.database import Reader

    reader = Reader(s3_bucket='foo',
                    aws_access_key_id='asf3223r4',
                    aws_secret_access_key='234431324')  # alternatively, pass maxmind_license_key or set MAXMIND_LICENSE_KEY env var
    
    response = reader.city('1.128.0.0') 

    print(response)
```

Notice that the arguments to `Reader()` are different from Maxmind's API.
Instead of passing a filename, there are two additional optional arguments that specify the
auto-refresh interval and location to write the database locally on disk:
```
    reader = ispdatabase.Reader(..., refresh_days=14, cache_dir='/tmp')
```

## Build

You can build and install manually with the following command:
```
    VERSION="0.1.0" python setup.py install
```
where `0.1.0` should be replaced with whatever tag you checked out.

A conda build recipe is also provided (currently only works in Linux).  Assuming you have your
environment set up (see e.g. https://github.com/ActivisionGameScience/ags_conda_recipes.git),
you can build the package by running
```
    VERSION="0.1.0" conda build conda_recipe
```

## License

All files are licensed under the BSD 3-Clause License as follows:
 
> Copyright (c) 2016, Activision Publishing, Inc.  
> All rights reserved.
> 
> Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
> 
> 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
>  
> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
>  
> 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
>  
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

