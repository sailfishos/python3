#
# SailfishOS Python 3 spec file
#
# adapted from: spec file for package python3-base
# Copyright (c) 2013 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.
#
# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

Name:           python3-base
BuildRequires:  autoconf-archive
BuildRequires:  automake
BuildRequires:  bzip2-devel
BuildRequires:  fdupes
BuildRequires:  glibc-headers
BuildRequires:  libffi-devel
BuildRequires:  openssl-devel
BuildRequires:  pkgconfig
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
# The RPM related dependencies bring nothing when building main python
# project, that is why we need to explicitly depend rpm generators.
# When bootstrapping python3, we need to build setuptools.
# but setuptools BR python3-devel and that brings in python3-rpm-generators;
# python3-rpm-generators needs python3-setuptools, so we cannot have it yet.
#
# Procedure: https://fedoraproject.org/wiki/SIGs/Python/UpgradingPython
#
%if %{?py_bootstrap:0}%{!?py_bootstrap:1}
BuildRequires:  python3-rpm-generators
%endif

Url:            https://github.com/sailfishos/python3
Summary:        Python3 Interpreter
License:        Python
Version:        3.11.14
Release:        0
Source0:        %{name}-%{version}.tar.gz
Source1:        python3-rpmlintrc
# skip-sem-test.patch
# Disables semaphore test. OBS arm build environment doesn't have
# /dev/shm mounted, so the test fails, crippling multiprocessing
# support for real devices.
Patch1:         0001-Skip-semaphore-test.patch
# Disable parallel compileall in make install.
Patch2:         0002-Disable-parallel-compileall-in-make-install.patch
# Fixup distutils/unixccompiler.py to remove standard library path from rpath:
Patch3:         0003-00001-Fixup-distutils-unixccompiler.py-to-remove-sta.patch
# Ensurepip should honour the value of $(prefix)
Patch4:         0004-bpo-31046-ensurepip-does-not-honour-the-value-of-pre.patch
# Restore pyc to TIMESTAMP invalidation mode as default
Patch5:         0005-00328-Restore-pyc-to-TIMESTAMP-invalidation-mode-as-.patch
# PATCH-FEATURE-UPSTREAM distutils-reproducible-compile.patch gh#python/cpython#8057 mcepl@suse.com
# Improve reproduceability
Patch6:         0006-Improve-reproduceability-patch-from-OpenSUSE.patch

%define         python_version  3.11
%define         python_version_abitag   311
%define         python_version_soname   3_11
%define         sitedir         %{_libdir}/python%{python_version}

# Some files are named so that they have this platform triplet
%ifarch %{arm}
%define armsuffix hf
%endif
%define		platform_triplet %{_arch}-%{_os}%{?_gnu}%{?armsuffix}

# soname ABI tag defined in PEP 3149
%define         so_version %{python_version_soname}1_0
%define dynlib() %{sitedir}/lib-dynload/%{1}.cpython-%{python_version_abitag}-%{platform_triplet}.so

# Disable automatic bytecompilation. The python3 binary is not yet be
# available in /usr/bin when Python is built. Also, the bytecompilation fails
# on files that test invalid syntax.
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Requires:       python3-libs = %{version}-%{release}

%description
Python is an interpreted, object-oriented programming language, and is
often compared to Tcl, Perl, Scheme, or Java.

If you want to install third party modules using distutils, you need to
install python-devel package.


Authors:
--------
    Guido van Rossum <guido@python.org>


%package -n python3-devel
Requires:       %{name} = %{version}
Requires:       pkgconfig(libcrypt)
# The RPM related dependencies bring nothing to a non-RPM Python developer
# But we want them when packages BuildRequire python3-devel
%if 0%{?no_rpm_conditional_requires}
Requires:       python-rpm-macros
Requires:       python3-rpm-macros
Requires:       python3-rpm-generators
%else
Requires:       (python-rpm-macros if rpm-build)
Requires:       (python3-rpm-macros if rpm-build)
%endif
# rpm-build needs python3-rpm-generators and python3-setuptools when python3-devel
# is installed but not otherwise. Putting this conditional Requires in python3-devel
# means that rpm-build does not have to know about python specific stuff.
# See https://bugzilla.redhat.com/show_bug.cgi?id=1410631 for rpm-build discussion
# and https://rpm.org/user_doc/boolean_dependencies.html for conditional Requires.
%if %{?py_bootstrap:0}%{!?py_bootstrap:1}
%if 0%{?no_rpm_conditional_requires}
Requires:       python3-rpm-generators
Requires:       python3-setuptools
%else
Requires:       (python3-rpm-generators if rpm-build)
Requires:       (python3-setuptools if rpm-build)
%endif
%endif
Summary:        Include Files and Libraries Mandatory for Building Python Modules

%description -n python3-devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.

This package contains header files, a static library, and development
tools for building Python modules, extending the Python interpreter or
embedding Python in applications.

This also includes the Python distutils, which were in the Python
package up to version 2.2.2.


%package -n python3-testsuite
Requires:       %{name} = %{version}
Summary:        Unit tests for Python and its standard library

%description -n python3-testsuite
Unit tests that are useful for verifying integrity and functionality
of the installed Python interpreter and standard library.
They are a documented part of stdlib, as a module 'test'.


%package -n python3-libs
Summary:        Python Interpreter shared library
Obsoletes:      libpython3_4m1_0
Obsoletes:      libpython3_81_0

%description -n python3-libs
Python is an interpreted, object-oriented programming language, and is
often compared to Tcl, Perl, Scheme, or Java.

This package contains libpython shared library for embedding in
other applications.


%package -n python3-doc
Requires:       %{name} = %{version}
Summary:        Documentation for %{name}

%description -n python3-doc
This package provides man pages for %{name}.


%prep
%autosetup -p1 -n %{name}-%{version}/upstream

# drop Autoconf version requirement
sed -i 's/^AC_PREREQ/dnl AC_PREREQ/' configure.ac

%build
# use rpm_opt_flags
export OPT="%{optflags}"

touch Makefile.pre.in

autoreconf -fi
# prevent make from trying to rebuild asdl stuff, which requires existing python installation
touch Parser/asdl* Python/Python-ast.c Include/Python-ast.h

# Disable some modules
touch Modules/Setup
cat <<EOF >> Modules/Setup
*disabled*
_dbm
_gdbm
nis
_tkinter
_uuid
readline
_curses
_curses_panel
_sqlite3
EOF

./configure \
    --with-platlibdir=%{_lib} \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --docdir=%{_docdir}/python \
    --enable-ipv6 \
    --enable-shared \
    --with-ensurepip=no \
    --with-dbmliborder=bdb \
    --with-system-ffi=yes

LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH \
    %make_build

%install
# replace rest of /usr/local/bin/python or /usr/bin/python2.5 or /usr/bin/python3m with /usr/bin/python3
find . -path "./Parser" -prune \
    -o -path "./Python/makeopcodetargets.py" -prune \
    -o -name '*.py' -type f -print0 \
| xargs -r -0 grep -lE '^#! *(/usr/.*bin/(env +)?)?python' \
| xargs -r sed -r -i -e '1s@^#![[:space:]]*(/usr/(local/)?bin/(env +)?)?python([0-9]+(\.[0-9]+)?)?[m]?@#!/usr/bin/python3@'
# the grep inbetween makes it much faster

# install it
%make_install

# remove .a
find ${RPM_BUILD_ROOT} -name "*.a" -exec rm {} ";"

# remove the rpm buildroot from the install record files
find ${RPM_BUILD_ROOT} -name 'RECORD' -print0 | \
    xargs -r -0 sed -i -e "s#${RPM_BUILD_ROOT}##g"

# install "site-packages" and __pycache__ for third parties
install -d -m 755 ${RPM_BUILD_ROOT}%{sitedir}/site-packages
install -d -m 755 ${RPM_BUILD_ROOT}%{sitedir}/site-packages/__pycache__
%if "%{_lib}" == "lib64"
# The 64-bit version needs to create "site-packages" in /usr/lib/ (for
# pure-Python modules) as well as in /usr/lib64/ (for packages with extension
# modules).
# Note that rpmlint will complain about hardcoded library path;
# this is intentional.
mkdir -p ${RPM_BUILD_ROOT}%{_prefix}/lib/python%{python_version}/site-packages/__pycache__
%endif

# Idle (Tk-based IDE, not useful on mobile)
rm -f \
    $RPM_BUILD_ROOT%{_bindir}/idle3 \
    $RPM_BUILD_ROOT%{_bindir}/idle%{python_version}
rm -rf $RPM_BUILD_ROOT/%{sitedir}/idlelib

# Other Tk stuff
rm -rf $RPM_BUILD_ROOT/%{sitedir}/tkinter
rm -rf $RPM_BUILD_ROOT/%{sitedir}/turtledemo

# overwrite the copied binary with a link
ln -sf python%{python_version} ${RPM_BUILD_ROOT}%{_bindir}/python3

# replace duplicate .pyo/.pyc with hardlinks
%fdupes $RPM_BUILD_ROOT/%{sitedir}

# remove extra copy of license text
rm -f $RPM_BUILD_ROOT/%{sitedir}/LICENSE.txt

# documentation
export PDOCS=${RPM_BUILD_ROOT}%{_docdir}/%{name}
install -d -m 755 $PDOCS
install -c -m 644 README.rst                        $PDOCS/

# remove .exe files
find $RPM_BUILD_ROOT%{sitedir}/ -type f -name '*.exe' -delete


%files -n python3-doc
%docdir %{_docdir}/%{name}
%{_docdir}/%{name}/README.rst
%{_mandir}/man1/python3.1*
%{_mandir}/man1/python%{python_version}.1*

%post -n python3-libs -p /sbin/ldconfig

%postun -n python3-libs -p /sbin/ldconfig

%files -n python3-libs
%{_libdir}/libpython%{python_version}.so.*

%files -n python3-devel
%{_libdir}/python%{python_version}/config-%{python_version}-%{platform_triplet}
%{_libdir}/libpython%{python_version}.so
%{_libdir}/libpython3.so
%{_libdir}/pkgconfig/*
%{_prefix}/include/python%{python_version}
%defattr(755, root, root)
%{_bindir}/python%{python_version}-config
%{_bindir}/python3-config
%{_bindir}/2to3
%{_bindir}/2to3-%{python_version}

%files -n python3-testsuite
%{sitedir}/test
%{sitedir}/*/test
%{sitedir}/*/tests
%{dynlib _ctypes_test}
%{dynlib _testcapi}
%{dynlib _testclinic}

%files
%license LICENSE
# binary parts
%dir %{sitedir}/lib-dynload
%{dynlib array}
%{dynlib audioop}
%{dynlib binascii}
%{dynlib _bisect}
%{dynlib cmath}
%{dynlib _codecs_cn}
%{dynlib _codecs_hk}
%{dynlib _codecs_iso2022}
%{dynlib _codecs_jp}
%{dynlib _codecs_kr}
%{dynlib _codecs_tw}
%{dynlib _crypt}
%{dynlib _csv}
%{dynlib _ctypes}
%{dynlib _datetime}
%{dynlib _decimal}
%{dynlib _elementtree}
%{dynlib fcntl}
%{dynlib grp}
%{dynlib _heapq}
%{dynlib _json}
%{dynlib _lsprof}
%{dynlib _lzma}
%{dynlib math}
%{dynlib mmap}
%{dynlib _multibytecodec}
%{dynlib _multiprocessing}
%{dynlib ossaudiodev}
%{dynlib _pickle}
%{dynlib _posixsubprocess}
%{dynlib _random}
%{dynlib resource}
%{dynlib select}
%{dynlib _socket}
%{dynlib spwd}
%{dynlib _struct}
%{dynlib syslog}
%{dynlib termios}
%{dynlib _typing}
%{dynlib _testbuffer}
%{dynlib unicodedata}
%{dynlib zlib}
%{dynlib _bz2}
%{dynlib _hashlib}
%{dynlib _ssl}
%{dynlib pyexpat}
%{dynlib _queue}
%{dynlib _testmultiphase}
%{dynlib _xxtestfuzz}
%{dynlib xxlimited_35}
%{dynlib _zoneinfo}
# hashlib fallback modules
%{dynlib _md5}
%{dynlib _sha1}
%{dynlib _sha256}
%{dynlib _sha512}
%{dynlib _sha3}
%{dynlib xxlimited}
# new in python 3.4
%{dynlib _asyncio}
%{dynlib _opcode}
%{dynlib _testimportmultiple}
# new in python 3.6
%{dynlib _blake2}
# new in python 3.7
%{dynlib _contextvars}
# new in python 3.8
%{dynlib _posixshmem}
%{dynlib _statistics}
%{dynlib _testinternalcapi}
%{dynlib _xxsubinterpreters}
# python parts
%dir %{sitedir}
%dir %{sitedir}/site-packages
%exclude %{sitedir}/*/test
%exclude %{sitedir}/*/tests
%{sitedir}/*.py
%{sitedir}/ctypes
%{sitedir}/collections
%{sitedir}/concurrent
%{sitedir}/distutils
%{sitedir}/email
%{sitedir}/encodings
%{sitedir}/ensurepip
%{sitedir}/html
%{sitedir}/xml
%{sitedir}/xmlrpc
%{sitedir}/http
%{sitedir}/importlib
%{sitedir}/json
%{sitedir}/lib2to3
%{sitedir}/logging
%{sitedir}/multiprocessing
%{sitedir}/pydoc_data
%{sitedir}/re
%{sitedir}/tomllib
%{sitedir}/unittest
%{sitedir}/urllib
%{sitedir}/venv
%{sitedir}/wsgiref
%{sitedir}/zoneinfo
%{sitedir}/sqlite3
%{sitedir}/dbm
%{sitedir}/curses
%{sitedir}/site-packages/README.txt
%{sitedir}/__phello__
%{sitedir}/__pycache__
%if "%{_lib}" == "lib64"
%attr(755, root, root) %dir %{_prefix}/lib/python%{python_version}
%attr(755, root, root) %dir %{_prefix}/lib/python%{python_version}/site-packages
%attr(755, root, root) %dir %{_prefix}/lib/python%{python_version}/site-packages/__pycache__
%endif
# new in python 3.4
%{sitedir}/asyncio
%{sitedir}/site-packages/__pycache__
# executables
%attr(755, root, root) %{_bindir}/pydoc%{python_version}
%attr(755, root, root) %{_bindir}/python%{python_version}
# links to copy
%{_bindir}/pydoc3
%{_bindir}/python3
