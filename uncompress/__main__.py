import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uncompress

if __name__ == '__main__':
    uncompress.run_cmd_main()