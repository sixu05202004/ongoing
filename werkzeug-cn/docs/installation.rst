============
安装
============

Werkzeug 需要至少 Python 2.6 才能正常工作。如果你需要支持旧的版本的话，你可以下载 Werkzeug 旧的版本，但是我们强烈不建议这么做。Werkzeug 目前实验性地支持 Python 3。对 Python 3 支持的更多的信息请参阅 :ref:`python3`。


安装一个发布版本
=============================

作为一个 Python egg (通过 easy_install 或者 pip)
---------------------------------------------------

你可以用 `easy_install`_ 安装最新版本的 Werkzeug::

    easy_install Werkzeug

或者你也可以用 pip::

    pip install Werkzeug

无论哪种方式我们都强烈建议和 :ref:`virtualenv` 配合使用这些工具。

这会在你的 Python 安装目录中的 `site-packages` 文件夹安装一个 Werkzeug egg。


从 tarball 版本安装
-------------------------

1.  从 `download page`_ 中下载最新的 tarball
2.  解压 tarball
3.  ``python setup.py install``

需要注意地是如果你还没有安装 `setuptools`_ 的话，最后一个命令将会自动地下载以及安装它。当然这需要有网络连接。

这将会把 Werkzeug 安装到你的 Python 安装目录中的 `site-packages` 文件夹。


安装开发版本
==================================

1.  安装 `Git`_
2.  ``git clone git://github.com/mitsuhiko/werkzeug.git``
3.  ``cd werkzeug``
4.  ``pip install --editable .``

.. _virtualenv:

virtualenv
==========

Virtualenv 可能是你想要在开发中，同样在生产环境上(如果你可以使用 shell 的话)使用的东东。

Virtualenv 能够解决什么问题？如果你像我一样喜欢 Python 的话，除了基于 Werkzeug 的 web 应用，你有更多的机会在其它项目上使用 Python。但是你有越多的项目，就越有可能需要在不同的 Python 版本上工作，或者至少需要在不同版本的 Python 库上工作。让我们面对现实；常常有些库是向后不兼容，并且任何一个正式的应用不依赖任何库是不可能的。因此，如果你的两个或者更多的项目存在冲突的依赖你怎么办了？

Virtualenv 拯救了我们！它基本上能够允许多个 Python 并列安装，每一个 Python 对应一个项目。Virtualenv 并不是实际安装单独的 Python 副本，只是提供了一种巧妙的方式保持不同项目之间环境的隔离。

因此让我们看看 virtualenv 如何工作的！

如果你是 Mac OS X 或者 Linux 用户，以下两个命令中任何一个都能为你服务::

    $ sudo easy_install virtualenv

或者甚至更好使用::

    $ sudo pip install virtualenv

这些命令中的任何一个都能在你的系统上安装 virtualenv。也许它甚至在你的包管理器中。如果你使用 Ubuntu，试着::

    $ sudo apt-get install python-virtualenv

如果你在 Windows 上并且没有 `easy_install` 命令，你必须首先安装它。一旦安装了，运行上面一样的命令，但是没有 `sudo` 前缀。

一旦你已经安装了 virtualenv，启动一个 shell 并且创建你自己的环境。我通常创建一个项目文件夹并且里面有一个 `env` 文件夹::

    $ mkdir myproject
    $ cd myproject
    $ virtualenv env
    New python executable in env/bin/python
    Installing setuptools............done.

现在，只要你想要在一个项目上工作，你只必须激活相应的环境。在 OS X 和 Linux 上，请执行以下操作::

    $ . env/bin/activate

(注意在点和脚本名之间的空格。点意味着这个脚本应该在当前 shell 的上下文中运行。如果这个命令在你的 shell 上不起作用的话，试着用 ``source`` 代替点)

如果你是一个 Windows 用户的话，下面的命令是适合你的::

    $ env\scripts\activate

无论哪种方式，现在你应该可以使用你的 virtualenv (看看你的 shell 提示符已经变更为显示的 virtualenv)。

现在你可以输入以下的命令在你激活的 virtualenv 中获取 Werkzeug::

    $ pip install Werkzeug

几秒钟后 Werkzeug 就安装好了。

.. _download page: https://pypi.python.org/pypi/Werkzeug
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _Git: http://git-scm.org/
