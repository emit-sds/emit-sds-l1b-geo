#=================================================================
# A few things that are common to all our configure files.

AC_DEFUN([USE_GEOCAL_SKELETON_COMMON],[
AC_REQUIRE([AC_CONFIG_AUX_DIR_DEFAULT])
 AC_REQUIRE([AC_PROG_CC])
# For some bizarre reason, this doesn't fail if there isn't a C++ compiler.
# This seems to be a bug, which had some discussion on the forums a while back
# (see http://lists.gnu.org/archive/html/bug-autoconf/2010-05/msg00001.html),
# but apparently hasn't been fixed. We work around this by checking if
# the CXX program is actually on the system.
AC_REQUIRE([AC_PROG_CXX])
# First check for CXX directly, in case the file path was given
if test -f "$CXX" && test -x "$CXX"; then
    HAVE_CXX=yes
else
   # Then check on path
   AC_CHECK_PROG(HAVE_CXX, $CXX, yes, no)
fi
if test "$HAVE_CXX" = "no"; then
   AC_MSG_ERROR([Could not find a c++ compiler]);
fi

# We need to have csh to run things like vicarb
AC_CHECK_PROG(HAVE_CSH, csh, yes, no)
if test "$HAVE_CSH" = "no"; then
   AC_MSG_ERROR([Could not find csh, which is required for programs such as vicar]);
fi

# We use a few GNU make specific things, so make sure we have gnu make
AX_CHECK_GNU_MAKE()
if test "$_cv_gnu_make_command" = "" ; then
   AC_MSG_ERROR([Could not find a gnu version of make]);
fi

AC_COPYRIGHT(
[Copyright 2020, California Institute of Technology. 
ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.])
# The obscure looking tar-pax here sets automake to allow file names longer
# than 99 characters to be included in the dist tar. See
# http://noisebleed.blogetery.com/2010/02/27/tar-file-name-is-too-long-max-99/#howtofixit
AM_INIT_AUTOMAKE([1.9 tar-pax])
AM_MAINTAINER_MODE
AC_PROG_LIBTOOL
# Don't need these yet
AC_PROG_CXX
# AC_PROG_LN_S
# AC_COPY_DIR

AC_PREFIX_DEFAULT([`pwd`/install])
AC_PROG_CC

AM_PROG_CC_C_O
AC_ENABLE_DEBUG

#=================================================================
# Start allowing code that requires newer version of compilers.
# C++ 11 in particular has been around for a long time, and we
# should probably be able to depend on this being available.
#
# For now, don't require any of this - we'll compile code with
# HAVE_CXX11 etc. We may relax this over time.
#=================================================================

AX_CXX_COMPILE_STDCXX([11], [ext], [optional])
# Don't currently have 14 or 17 code, but could add tests if this
# before useful

#=================================================================
# Test if we are using GCC compiler. Some flags get set in the 
# Makefile that should only be set for GCC.
#=================================================================

AM_CONDITIONAL([HAVE_GCC], [test "$GCC" = yes])

#=================================================================
# Add prefix, THIRDPARTY, and /opt/afids_support for pkgconfig file

PKG_PROG_PKG_CONFIG

if test "x$THIRDPARTY" = x ; then
  pkg_extra_path=\${prefix}/lib/pkgconfig:/opt/afids_support/lib/pkgconfig
else
  pkg_extra_path=\${prefix}/lib/pkgconfig:$THIRDPARTY/lib/pkgconfig:/opt/afids_support/lib/pkgconfig
fi
if test "x$CONDA_PREFIX" != x; then
   pkg_extra_path=$CONDA_PREFIX/lib/pkgconfig:${pkg_extra_path}
fi
if test "x$PKG_CONFIG_PATH" = x; then
  PKG_CONFIG_PATH=$pkg_extra_path
else
  PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$pkg_extra_path
fi
export PKG_CONFIG_PATH

AC_SUBST([pkgconfigdir], [${libdir}/pkgconfig])

AC_ARG_WITH([geocal],
AS_HELP_STRING([--with-geocal=DIR], [give directory where geocal can be found (optional, default is /pkg/afids/geocal_latest)]), [ ac_geocal_dir="$withval" ], [ ac_geocal_dir="/pkg/afids/geocal_latest" ])
PKG_CONFIG_PATH=$ac_geocal_dir/lib/pkgconfig:$PKG_CONFIG_PATH
PKG_CHECK_MODULES([GEOCAL], [geocal])
PKG_CHECK_VAR([GEOCAL_SWIG_CFLAGS], [geocal], [swig_cflags])
PKG_CHECK_VAR([geocaldir], [geocal], [prefix])

])
