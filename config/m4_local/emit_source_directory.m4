# Stuff for EMIT
# We have the top directory for geocal as a variable. This allows the
# full AFIDS system to include this in a subdirectory.

AC_DEFUN([EMIT_SOURCE_DIRECTORY],[
AC_SUBST([swigrules], [swig_rules])
AC_SUBST([srcemitbin], [bin])
AC_SUBST([srcpython], [python])
AC_SUBST([l1b_geo_src], [l1b_geo])
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
AC_SUBST([pythondocdir], [\${prefix}/share/doc/emit/python])
AC_SUBST([emitswigincdir], [\${prefix}/share/emit/swig])
AC_SUBST([swigincdir], [\${prefix}/share/emit/swig])
AC_SUBST([installemitdir], [\${prefix}])
AC_SUBST([emitpkgpythondir],[\${prefix}/\${pythondir}/emit])
])
