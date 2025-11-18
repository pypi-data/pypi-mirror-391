import git
from .options import *
from .fileutils import *
from .templates import *

#-------------------------------------------------------------------------------#
# Main
#-------------------------------------------------------------------------------#

def main():
    args, dargs = parse_args()

    # cmake
    write(args.root / 'CMakeLists.txt', TOPLEVEL_CMAKELISTS.format(**dargs))
    write(args.root / 'modules/CMakeLists.txt',
        MODULES_CMAKELISTS.format(**dargs))
    write(args.root / 'modules/cmmn' / 'CMakeLists.txt',
        CMMN_CMAKELISTS.format(**dargs))
    write(args.root / 'modules/spec' / 'CMakeLists.txt',
        SPEC_CMAKELISTS.format(**dargs))
    write(args.root / 'app' / 'CMakeLists.txt', APP_CMAKELISTS.format(**dargs))

    # modules
    write(args.root / 'modules' / 'config.hh.in',
        MODULES_CONFIG.format(**dargs))
    # cmmn
    write(args.root / 'modules/cmmn' / 'exports.hh',
        CMMN_EXPORTS.format(**dargs))
    write(args.root / 'modules/cmmn' / 'types.hh', CMMN_TYPES.format(**dargs))

    # spec
    write(args.root / 'modules/spec' / 'control.hh',
        SPEC_CONTROL.format(**dargs))
    write(args.root / 'modules/spec' / 'exports.hh',
        SPEC_EXPORTS.format(**dargs))
    write(args.root / 'modules/spec' / 'types.hh', SPEC_TYPES.format(**dargs))

    # app
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
    copy_resource('support/env.yaml', args.root)

    if(args.git):
        repo = git.Repo.init(args.root)
        repo.index.add(['*', '.*'])
        repo.index.commit('Initial Check-In')
        copy_resource('.gitignore', args.root)
