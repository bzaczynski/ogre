# [ogre](https://github.com/bzaczynski/ogre)

Build beautiful .pdf reports from [Ognivo](https://www.banki.kir.pl/ognivo/) query results.

### Download

Source code:

```
$ git clone https://github.com/bzaczynski/ogre.git
```

Binary packages:

* [Linux](https://www.dropbox.com/s/c8nwqq5p0pdprtw/ogre-1.0.0rc2-linux.pex?dl=0)
* [Windows](https://www.dropbox.com/s/ldub8gjb9s60wyi/ogre-1.0.0rc2-windows.pex?dl=0)

### Requirements

#### Python

Download and install [Python 2.7](https://www.python.org/downloads/) if not already available on your operating system.

For advanced use cases described later you will also need to specify the location of Python interpreter via the `PATH` environment variable. However, you can skip this step for now.

#### PATH

By default Python installer does not modify environment variables on Windows. To manually add the location of Python interpreter to user's `PATH` environment variable open the command line and type:

```
C:\> SETX PATH "%PATH%;C:\Python27\;C:\Python27\Scripts"
```

To make Python work for all users run the command line as administrator and type the same command with the `/M` flag which will affect the corresponding `PATH` system variable instead.

### Installation

If you have downloaded one of the binary distributions targeting your platform then you are ready to go. On Windows you just have to associate `*.pex` file extension with a Python interpreter by providing the path to `python.exe` when prompted.

Building from source requires a few additional steps on the other hand.

#### Requirements

##### Package Managers

Note these should be already bundled as part of the standard Python installation if you have downloaded a recent version of the interpreter.

Install [setuptools](https://pypi.python.org/pypi/setuptools#installation-instructions) if not already available:

```
$ curl https://bootstrap.pypa.io/ez_setup.py | python
```

Install [pip](http://www.pip-installer.org/en/latest/installing.html) if not already available:

```
$ curl https://bootstrap.pypa.io/get-pip.py | python
```

Make sure you have the latest versions of both:

```
$ sudo pip install pip setuptools --upgrade
```

On Windows manually download both [ez_setup.py](https://bootstrap.pypa.io/ez_setup.py) and [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and execute them as python scripts from the command line.

##### Virtual Environment

Although not strictly required it is still advisable to use a dedicated virtual environment for the installation. It may be more convenient to use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) on top of [virtualenv](https://virtualenv.pypa.io/en/stable/) but that requires some extra configuration, which will not be discussed here.

```
$ pip install virtualenv virtualenvwraper
```

##### C++ Compiler

On Windows you will need to install [Microsoft Visual C++ Compiler for Python 2.7](http://aka.ms/vcpython27) since this program depends on native libraries which need to be built from source.

#### System-wide Installation

This will install the application into the Python interpreter itself:

```
$ sudo python setup.py install
```

#### Virtual Environment Installation

Using [virtualenv](https://virtualenv.pypa.io/en/stable/):

```
$ virtualenv venv
$ . venv/bin/activate
(venv) $ python setup.py install
```

Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

```
$ mkvirtualenv venv
(venv) $ python setup.py install
```

### Uninstallation

```
$ pip uninstall ogre
```

### Usage

#### Binary

Copy `ogre.pex` to a directory where Ognivo XML responses have been downloaded to and execute it, e.g. by double clicking the icon.

This will recursively scan current working directory for well-formed and valid Ognivo XML responses and then process them to generate and open a PDF report ready for printing.

For more advanced options use the terminal, e.g.

```
$ python ogre.pex --help
```

#### Source

Activate virtual environment with ogre installed if not using the system-wide installation:

```
$ workon venv
```

or

```
C:\> venv\Scripts\activate
```

Change directory to where Ognivo XML responses have been downloaded to, e.g.

```
(venv) $ cd ~/Downloads
```

Execute the script:

```
(venv)~/Downloads $ ogreport.py
```

#### Parameters

The script as well as the binary package take an optional positional argument with the resulting file name. If omitted the file will be named after the current timestamp. Should the file with the given name already exist use the `--force` or `-f` flag to enforce overwrite:

```
$ ogreport.py filename.pdf -f
```

or

```
$ python ogre.pex filename.pdf -f
```

#### Configuration

To display available configuration options run the script with the `--debug` or `-d` flag.

The program comes with a default configuration, which includes unique bank code prefixes for instance. To augment or modify the defaults create a file named `config.ini` in the current working directory where the script will be started from. As long as the file conforms to INI format it will be detected automatically and used to override existing property values.

Alternatively specify an arbitrary path to the custom configuration file with the `--config` or `-c` option, e.g.

```
$ ogreport.py --config /path/to/mycfg.ini
```

or

```
$ python ogre.pex --config /path/to/mycfg.ini
```

Note that all three configuration sources can be used simultaneously. They are processed in the following order, meaning the next value overwrites the previous one:

1. embedded default config
2. `config.ini` located in the current working directory
3. file specified with `--config /path/to/config.ini`

### Building Binary Package

**WARNING!**

The name *ogre* is already taken by another project on [PyPI](https://pypi.python.org/pypi) which takes precedence over the local project via pip/pex. In order to force the packaging of a local project instead of the one from PyPI an explicit version of *1.0.0rc1* is given below.

#### Linux

```
$ mkvirtualenv venv
(venv) $ pip install pex "setuptools<20.11,>=2.2"
(venv) $ python setup.py bdist_wheel
(venv) $ pex "ogre==1.0.0rc2" -f dist -r requirements.txt -c ogreport.py -o ogre-1.0.0rc2-linux.pex
```

#### Windows

```
C:\> pip install virtualenv
C:\> virtualenv venv
C:\> venv\Scripts\activate
(venv) C:\> pip install pex
(venv) C:\> python setup.py bdist_wheel
(venv) C:\> pex "ogre==1.0.0rc2" -f dist -r requirements.txt -c ogreport.py -o ogre-1.0.0rc2-windows.pex
```

### Author

Bartosz Zaczynski

### License

This project is licensed under the [MIT License](https://raw.githubusercontent.com/bzaczynski/ogre/master/LICENSE).
