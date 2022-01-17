# Have defaults for location of afids and geocal, but let the user override
# these

AC_DEFUN([EMIT_LOCATION],
[
AC_ARG_WITH([test-data],
AS_HELP_STRING([--with-test-data=DIR], [give directory where end to end test data can be found (optional, default is /beegfs/store/shared/emit-test-data)]), [ ac_test_data_dir="$withval" ], [ ac_test_data_dir="/beegfs/store/shared/emit-test-data" ])
AC_SUBST([testdatadir], ["$ac_test_data_dir"])

])
