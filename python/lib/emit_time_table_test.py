from .emit_time_table import *
from test_support import *
import geocal

def test_emit_time_table(time_table_fname):
    tt = EmitTimeTable(time_table_fname)
    #print(tt)
    # Trivial test, we are just making sure we can access the orbit
    assert tt.max_time - tt.min_time > 10.0

def test_write_emit_time_table(isolated_dir):
    t = geocal.Time.parse_time("2020-10-01T12:01:02.00Z");
    tt = geocal.ConstantSpacingTimeTable(t+1, t + 100, 1.0)
    EmitTimeTable.write_file("line_time.nc", tt)
    tt = EmitTimeTable("line_time.nc")
    # We add 1 second padding at the beginning of the time table to allow
    # for interpolation
    assert abs(tt.min_time - t) < 0.01
    assert abs(tt.max_time - (t+100+1)) < 0.01
    
    
    



