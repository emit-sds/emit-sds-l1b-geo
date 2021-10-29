from .emit_time_table import *
from test_support import *
import geocal

def test_emit_time_table(isolated_dir):
    t = geocal.Time.parse_time("2020-10-01T12:01:02.00Z");
    tt = geocal.ConstantSpacingTimeTable(t, t + 100, 1.0)
    e_tt = EmitTimeTable()
    e_tt.write_time_table(tt, "line_time.nc")
    e_tt.read_time_table("line_time.nc")
    print(e_tt.tt)
    
    
    



