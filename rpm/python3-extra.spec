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

Name:           python3-extra
BuildRequires:  automake
BuildRequires:  readline-devel
BuildRequires:  python3-devel
BuildRequires:  sqlite-devel
Url:            http://www.python.org/
Summary:        Python3 Interpreter extra modules
License:        Python
Version:        3.8.1
Release:        0
Source0:        %{name}-%{version}.tar.gz
Source1:        python3-rpmlintrc
# skip-sem-test.patch
# Disables semaphore test. OBS arm build environment doesn't have
# /dev/shm mounted, so the test fails, crippling multiprocessing
# support for real devices.
Patch0:         0001-Skip-semaphore-test.patch
# Disable parallel compileall in make install.
Patch1:         0002-Disable-parallel-compileall-in-make-install.patch
# Fixup distutils/unixccompiler.py to remove standard library path from rpath:
Patch2:         0003-00001-Fixup-distutils-unixccompiler.py-to-remove-sta.patch
# Change the various install paths to use /usr/lib64/ instead or /usr/lib
# Only used when "%%{_lib}" == "lib64"
Patch3:         0004-00102-Change-the-various-install-paths-to-use-usr-li.patch
# Ensurepip should honour the value of $(prefix)
Patch4:         0005-bpo-31046_ensurepip_honours_prefix.patch

%description
Additional base modules for Python.

%define         python_version  3.8
%define         python_version_abitag   38
%define         python_version_soname   3_8
%define         sitedir         %{_libdir}/python%{python_version}

# Some files are named so that they have this platform triplet
%if %{_arch} == arm
%define armsuffix hf
%endif
%define         platform_triplet %{_arch}-%{_os}%{?_gnu}%{?armsuffix}

# soname ABI tag defined in PEP 3149
%define         so_version %{python_version_soname}1_0
%define dynlib() %{sitedir}/lib-dynload/%{1}.cpython-%{python_version_abitag}-%{platform_triplet}.so

%package -n python3-curses
Provides:       python%{python_version}dist(curses) = %{version}
Provides:       python3dist(curses) = %{version}
Requires:       python3-base = %{version}
Summary:        Python3 module for readline and ncurses

%description -n python3-curses
This package contains the readline and ncurses modules for Python.

%package -n python3-sqlite
Provides:       python%{python_version}dist(sqlite) = %{version}
Provides:       python3dist(sqlite) = %{version}
Provides:       python%{python_version}dist(sqlite3) = %{version}
Provides:       python3dist(sqlite3) = %{version}
Requires:       python3-base = %{version}
Summary:        Python3 module for sqlite

%description -n python3-sqlite
This package contains the sqlite module for Python.

%prep
%setup -q -n %{name}-%{version}/upstream

%patch0 -p1
%patch1 -p1
%patch2 -p1
%if "%{_lib}" == "lib64"
%patch3 -p1
%endif
%patch4 -p1

%build
# use rpm_opt_flags
export OPT="%{optflags}"

touch Makefile.pre.in

autoreconf -fi
# prevent make from trying to rebuild asdl stuff, which requires existing python installation
touch Parser/asdl* Python/Python-ast.c Include/Python-ast.h

# Disable all modules already compiled in python3-base, or otherwise unwanted
touch Modules/Setup
cat <<EOF >> Modules/Setup
*disabled*
_asyncio
_bisect
_blake2
_bz2
_codecs_cn
_codecs_hk
_codecs_iso2022
_codecs_jp
_codecs_kr
_codecs_tw
_contextvars
_crypt
_csv
_ctypes
_ctypes_test
_datetime
_decimal
_elementtree
_hashlib
_heapq
_json
_lsprof
_lzma
_md5
_multibytecodec
_multiprocessing
_opcode
_pickle
_posixshmem
_posixsubprocess
_queue
_random
_sha1
_sha256
_sha3
_sha512
_socket
_ssl
_statistics
_struct
_testbuffer
_testcapi
_testimportmultiple
_testinternalcapi
_testmultiphase
_uuid
_xxsubinterpreters
_xxtestfuzz
array
audioop
binascii
cmath
fcntl
grp
math
mmap
ossaudiodev
parser
pyexpat
resource
select
spwd
syslog
termios
unicodedata
xxlimited
zlib
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
    make %{?_smp_mflags} sharedmods

%install
make \
    OPT="%{optflags} -fPIC" \
    DESTDIR=$RPM_BUILD_ROOT \
    sharedinstall

# Remove installed binaries
rm -f $RPM_BUILD_ROOT%{_bindir}/*

%files -n python3-curses
%defattr(644, root, root, 755)
%license LICENSE
%{dynlib _curses}
%{dynlib _curses_panel}
%{dynlib readline}

%files -n python3-sqlite
%defattr(644, root, root, 755)
%license LICENSE
%{dynlib _sqlite3}
