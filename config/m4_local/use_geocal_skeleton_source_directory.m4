# Stuff for UseGeoCalSkeleton.
# We have the top directory for geocal as a variable. This allows the
# full AFIDS system to include this in a subdirectory.

AC_DEFUN([USE_GEOCAL_SKELETON_SOURCE_DIRECTORY],[
AC_SUBST([swigrules], [swig_rules])
AC_SUBST([srcuse_geocal_skeletonbin], [bin])
AC_SUBST([srcpython], [python])
AC_SUBST([srcscript], [script])
AC_SUBST([srclib], [lib])
AC_SUBST([srcpythonlib], [${srcpython}/lib])
AC_SUBST([srcpythonbin], [${srcpython}/bin])
AC_SUBST([docpythonsrc], [${srcpython}/doc])
AC_SUBST([testsupportsrc], [${srcpython}/test_support])
AC_SUBST([unittestdata], [unit_test_data])
AC_SUBST([pythonswigsrc], [bindings/python])
AC_SUBST([swigsrc], [bindings/python/swig])
AC_SUBST([srcpythonscript], [script])
AC_SUBST([pythondocdir], [\${prefix}/share/doc/use_geocal_skeleton/python])
AC_SUBST([use_geocal_skeletonswigincdir], [\${prefix}/share/use_geocal_skeleton/swig])
AC_SUBST([swigincdir], [\${prefix}/share/use_geocal_skeleton/swig])
AC_SUBST([installuse_geocal_skeletondir], [\${prefix}])
AC_SUBST([use_geocal_skeletonpkgpythondir],[\${prefix}/\${pythondir}/use_geocal_skeleton])
])
