// -*- mode: c++; -*-
// (Not really c++, but closest emacs mode)

//--------------------------------------------------------------
// This provides common functions etc. used throughout our SWIG
// code. This should get included at the top of each swig file.
//--------------------------------------------------------------

// The module actually gets overridden by SWIG command line options
// when we build. But we still need to supply this to get the
// directors=1 and allprotected=1 set.

%module(directors="1", allprotected="1") use_geocal_skeleton_swig

%include "geocal_common.i"

// Short cut for ingesting a base class
%define %use_geocal_skeleton_base_import(NAME)
%import(module="use_geocal_skeleton_swig.NAME") "NAME.i"
%enddef

%define %geocal_base_import(NAME)
%import(module="geocal_swig.NAME") "NAME.i"
%enddef

%define %use_geocal_skeleton_shared_ptr(TYPE...)
%geocal_shared_ptr(TYPE)
%enddef
