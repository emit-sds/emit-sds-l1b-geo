from .dummy import *
from test_support import *

def test_dummy():
    dummy_func()

def test_swig():
    '''Basic test, make sure we can create a EcostressScanMirror'''
    sm = EcostressScanMirror()
    assert sm.number_sample == 5400
    
