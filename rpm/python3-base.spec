#
# Mer Python 3 spec file
# https://build.merproject.org/project/show?project=mer-python3
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
BuildRequires:  automake
BuildRequires:  fdupes
BuildRequires:  pkgconfig
BuildRequires:  xz
BuildRequires:  zlib-devel
BuildRequires:  sqlite-devel
BuildRequires:  openssl-devel
BuildRequires:  bzip2-devel
BuildRequires:  xz-devel
BuildRequires:  glibc-headers
BuildRequires:  libffi-devel
Url:            http://www.python.org/
Summary:        Python3 Interpreter
License:        Python-2.0
Group:          Development/Languages/Python
Version:        3.8.1
Release:        0
Source0:        %{name}-%{version}.tar.gz
Source1:        python3-rpmlintrc
# To rebuild or extend the patch set apply these patches to upstream
# on a branch called sfos/<python-tag> using base provided in the
# first patch, rebase and regenerate using:
#  cd upstream && git format-patch --base=<python-tag> <python-tag>..sfos/<python-tag> -o ../rpm/
Patch0:         0001-configure-Skip-semaphore-test.patch
Patch1:         0002-Disable-parallel-compileall-in-make-install.patch

%define         python_version  3.8
%define         python_version_abitag   38
%define         python_version_soname   3_8
%define         sitedir         %{_libdir}/python%{python_version}

# Some files are named so that they have this platform triplet
%if %{_arch} == arm
%define armsuffix hf
%endif
%define		platform_triplet %{_arch}-%{_os}%{?_gnu}%{?armsuffix}

# soname ABI tag defined in PEP 3149
%define         so_version %{python_version_soname}1_0
%define dynlib() %{sitedir}/lib-dynload/%{1}.cpython-%{python_version_abitag}-%{platform_triplet}.so

Requires:       libpython%{so_version} = %{version}

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
Provides:       python3-2to3 = %{version}
Obsoletes:      python3-2to3 <= %{version}
Summary:        Include Files and Libraries Mandatory for Building Python Modules
Group:          Development/Languages/Python

%description -n python3-devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.

This package contains header files, a static library, and development
tools for building Python modules, extending the Python interpreter or
embedding Python in applications.

This also includes the Python distutils, which were in the Python
package up to version 2.2.2.


%package -n python3-testsuite
Requires:       python3-base = %{version}
Summary:        Unit tests for Python and its standard library
Group:          Development/Languages/Python

%description -n python3-testsuite
Unit tests that are useful for verifying integrity and functionality
of the installed Python interpreter and standard library.
They are a documented part of stdlib, as a module 'test'.


%package -n libpython%{so_version}
Summary:        Python Interpreter shared library
Group:          Development/Languages/Python
Obsoletes:      libpython3_4m1_0

%description -n libpython%{so_version}
Python is an interpreted, object-oriented programming language, and is
often compared to Tcl, Perl, Scheme, or Java.

This package contains libpython shared library for embedding in
other applications.


%package -n python3-doc
Summary:        Documentation for %{name}
Group:          Documentation
Requires:       python3-base = %{version}

%description -n python3-doc
This package provides man pages for %{name}.


%package -n python3-pip
Requires:       python3-base = %{version}
Summary:        Pip package manager
Group:          Development/Languages/Python

%description -n python3-pip
The pip package manager.


%package -n python3-setuptools
Requires:       python3-base = %{version}
Summary:        Setup tools for package distribution
Group:          Development/Languages/Python

%description -n python3-setuptools
The setup python tool to manage package distribution and installation.


%prep
%setup -q -n %{name}-%{version}/upstream

# skip-sem-test.patch
# Disables semaphore test. OBS arm build environment doesn't have
# /dev/shm mounted, so the test fails, crippling multiprocessing
# support for real devices.
%patch0 -p1
# Disable parallel compileall in make install.
%patch1 -p1

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
EOF

./configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --docdir=%{_docdir}/python \
    --enable-ipv6 \
    --enable-shared \
    --with-dbmliborder=bdb \
    --with-system-ffi=yes

LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH \
    make %{?_smp_mflags}

%install
# replace rest of /usr/local/bin/python or /usr/bin/python2.5 or /usr/bin/python3m with /usr/bin/python3
find . -path "./Parser" -prune \
    -o -path "./Python/makeopcodetargets.py" -prune \
    -o -name '*.py' -type f -print0 \
| xargs -r -0 grep -lE '^#! *(/usr/.*bin/(env +)?)?python' \
| xargs -r sed -r -i -e '1s@^#![[:space:]]*(/usr/(local/)?bin/(env +)?)?python([0-9]+(\.[0-9]+)?)?[m]?@#!/usr/bin/python3@'
# the grep inbetween makes it much faster

# install it
make \
    OPT="%{optflags} -fPIC" \
    DESTDIR=$RPM_BUILD_ROOT \
    install

# remove .a
find ${RPM_BUILD_ROOT} -name "*.a" -exec rm {} ";"

# remove the rpm buildroot from the install record files
find ${RPM_BUILD_ROOT} -name 'RECORD' -print0 | \
    xargs -r -0 sed -i -e "s#${RPM_BUILD_ROOT}##g"

# install "site-packages" and __pycache__ for third parties
install -d -m 755 ${RPM_BUILD_ROOT}%{sitedir}/site-packages
install -d -m 755 ${RPM_BUILD_ROOT}%{sitedir}/site-packages/__pycache__

# if pip is present on the system, ensurepip will not do anything
# so copying pip related-files by hand from the system.
if [ -f /usr/bin/pip3 ] ; then
    install /usr/bin/easy_install-%{python_version} /usr/bin/pip3 /usr/bin/pip%{python_version} ${RPM_BUILD_ROOT}%{_bindir}
    install /usr/lib/python%{python_version}/site-packages/easy_install.py ${RPM_BUILD_ROOT}%{sitedir}/site-packages
    cp -rp /usr/lib/python%{python_version}/site-packages/pip* ${RPM_BUILD_ROOT}%{sitedir}/site-packages
    cp -rp /usr/lib/python%{python_version}/site-packages/setuptools* ${RPM_BUILD_ROOT}%{sitedir}/site-packages
    cp -rp /usr/lib/python%{python_version}/site-packages/pkg_resources ${RPM_BUILD_ROOT}%{sitedir}/site-packages
fi

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

%clean
rm -rf $RPM_BUILD_ROOT

%files -n python3-doc
%docdir %{_docdir}/%{name}
%{_docdir}/%{name}/README.rst
%{_mandir}/man1/python3.1*
%{_mandir}/man1/python%{python_version}.1*

%post -n libpython%{so_version} -p /sbin/ldconfig

%postun -n libpython%{so_version} -p /sbin/ldconfig

%files -n libpython%{so_version}
%defattr(644, root,root)
%{_libdir}/libpython%{python_version}.so.*

%files -n python3-devel
%defattr(644, root, root, 755)
%{_libdir}/libpython%{python_version}.so
%{_libdir}/libpython3.so
%{_libdir}/pkgconfig/*
%{_prefix}/include/python%{python_version}
%exclude %{_prefix}/include/python%{python_version}/pyconfig.h
%defattr(755, root, root)
%{_bindir}/python%{python_version}-config
%{_bindir}/python3-config
%{_bindir}/2to3
%{_bindir}/2to3-%{python_version}

%files -n python3-testsuite
%defattr(644, root, root, 755)
%{sitedir}/test
%{sitedir}/*/test
%{dynlib _ctypes_test}
%{dynlib _testcapi}

# Cannot be packaged if pip is already installed on the system
# because ensurepip script do not install anything if pip is found
# in the path.
%files -n python3-pip
%defattr(644, root, root, 755)
%{sitedir}/ensurepip
%{sitedir}/site-packages/pip
%{sitedir}/site-packages/pip*.dist-info
# new in python 3.4
%attr(755, root, root) %{_bindir}/pip3
%attr(755, root, root) %{_bindir}/pip%{python_version}

%files -n python3-setuptools
%defattr(644, root, root, 755)
%{sitedir}/site-packages/setuptools
%{sitedir}/site-packages/setuptools*.dist-info
%{sitedir}/site-packages/pkg_resources
%{sitedir}/site-packages/easy_install.py
%{sitedir}/site-packages/__pycache__/easy_install*
# new in python 3.4
%attr(755, root, root) %{_bindir}/easy_install-%{python_version}

%files
%defattr(644, root, root, 755)
%license LICENSE
# makefile etc
# %%{sitedir}/config-%%{python_abi}-%%{platform_triplet}
%{_prefix}/include/python%{python_version}/pyconfig.h
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
%{dynlib parser}
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
%{dynlib _testbuffer}
%{dynlib unicodedata}
%{dynlib zlib}
%{dynlib _sqlite3}
%{dynlib _bz2}
%{dynlib _hashlib}
%{dynlib _ssl}
%{dynlib pyexpat}
%{dynlib _queue}
%{dynlib _testmultiphase}
%{dynlib _xxtestfuzz}
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
%{sitedir}/*.*
%{sitedir}/ctypes
%{sitedir}/collections
%{sitedir}/concurrent
%{sitedir}/distutils
%{sitedir}/email
%{sitedir}/encodings
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
%{sitedir}/unittest
%{sitedir}/urllib
%{sitedir}/venv
%{sitedir}/wsgiref
%{sitedir}/sqlite3
%{sitedir}/dbm
%{sitedir}/curses
%{sitedir}/site-packages/README.txt
%{sitedir}/__pycache__
# new in python 3.4
%{sitedir}/asyncio
%{sitedir}/site-packages/__pycache__
%exclude %{sitedir}/site-packages/__pycache__/easy_install*
# executables
%attr(755, root, root) %{_bindir}/pydoc%{python_version}
%attr(755, root, root) %{_bindir}/python%{python_version}
# links to copy
%{_bindir}/pydoc3
%{_bindir}/python3
