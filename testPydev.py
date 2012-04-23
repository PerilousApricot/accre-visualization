import clutter

stage = clutter.Stage
print stage
if 'Stage' in dir(clutter):
    print "Stage is in clutter"
print dir(clutter)