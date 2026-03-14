import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/hppmp/Workspace/nav_assignment_ws/install/trajectory_nav'
