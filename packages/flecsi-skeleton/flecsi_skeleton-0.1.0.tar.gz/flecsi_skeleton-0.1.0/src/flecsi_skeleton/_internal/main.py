import git
from .options import *
from .fileutils import *
from .templates import *

#-------------------------------------------------------------------------------#
# Main
#-------------------------------------------------------------------------------#

def main():
    args, dargs = parse_args()

    write(args.root / 'CMakeLists.txt', TOPLEVEL_CMAKELISTS.format(**dargs))
    write(args.root / 'spec' / 'CMakeLists.txt', SPEC_CMAKELISTS.format(**dargs))
    write(args.root / 'app' / 'CMakeLists.txt', APP_CMAKELISTS.format(**dargs))

    write(args.root / 'spec' / 'config.hh.in', SPEC_CONFIG.format(**dargs))
    write(args.root / 'spec' / 'control.hh', SPEC_CONTROL.format(**dargs))
    write(args.root / 'spec' / 'exports.hh', SPEC_EXPORTS.format(**dargs))
    write(args.root / 'spec' / 'types.hh', SPEC_TYPES.format(**dargs))

    write(args.root / 'app' / (args.name + '.cc'), APP_DRIVER.format(**dargs))
    write(args.root / 'app' / 'advance.hh', APP_ADVANCE.format(**dargs))
    write(args.root / 'app' / 'analyze.hh', APP_ANALYZE.format(**dargs))
    write(args.root / 'app' / 'finalize.hh', APP_FINALIZE.format(**dargs))
    write(args.root / 'app' / 'initialize.hh', APP_INITIALIZE.format(**dargs))
    write(args.root / 'app' / 'state.hh', APP_STATE.format(**dargs))
    write(args.root / 'app' / 'types.hh', APP_TYPES.format(**dargs))

    write(args.root / 'app/tasks' / 'initialize.hh',
        APP_TASK_INITIALIZE.format(**dargs))

    copy_resource('README.md', args.root)
    copy_resource('.clang-format', args.root)
    copy_resource('.gitignore', args.root)
    copy_resource('support/env.yaml', args.root)

    repo = git.Repo.init(args.root)
    repo.index.add(['*', '.*'])
    repo.index.commit('Initial Check-In')

