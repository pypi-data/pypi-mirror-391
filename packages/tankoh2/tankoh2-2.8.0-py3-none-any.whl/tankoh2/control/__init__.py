# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""package with scripts controlling the execution of tankoh2 features"""

if __name__ == "__main__":
    import sys

    sys.argv += ["--useBucklingCriterion", "--designName=exact2_large_designspace_buck"]
    from tankoh2.control.control_doe import main

    main()
