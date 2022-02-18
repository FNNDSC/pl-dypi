#!/usr/bin/env python

from    multiprocessing.spawn   import import_main_path
from    pathlib                 import Path
from    argparse                import ArgumentParser, Namespace
from    chris_plugin            import chris_plugin, PathMapper
from    loguru                  import logger

import  pudb

from    state                   import data
from    logic                   import behavior
from    control                 import action


Env             = data.CUBEinstance()
PLinputFilter   = action.PluginRun(env = Env)
CAW             = action.Caw(env = Env)

parser      = ArgumentParser(description='ChRIS DS plugin that creates responsive/dynamic compute trees based on some logic applied over the input space')
parser.add_argument(
            '-p', '--pattern', 
            default = '**/*',
            help    = 'pattern for file names to include'
)
parser.add_argument(
            '-d', '--dirsOnly',
            action  = 'store_true',
            default = False,
            help    = 'if specified, only filter directories, not files'
)
parser.add_argument(
            '-P', '--pipeline',
            default = '',
            help    = 'pipeline string to execute on filtered child node'
)
parser.add_argument(
            '-i', '--pluginInstanceID',
            default = '',
            help    = 'plugin instance ID from which to grow a tree'
)


def unconditionalPass(str_object: str) -> bool:
    '''
    If a more complex conditional is required, code it here.
    '''
    return True

def tree_grow(options: Namespace, input: Path, output: Path) -> dict:
    '''
    Based on some conditional of the <input> direct the
    dynamic "growth" of this feed tree from the parent node
    of *this* plugin.
    '''
    global Env, PLinputFilter, CAW

    conditional             = behavior.Filter()
    conditional.obj_pass    = unconditionalPass

    if conditional.obj_pass(str(input)):
        d_nodeInput         = PLinputFilter(str(input))
        if len(options.pipeline):
            d_caw           = CAW(d_nodeInput['branchInstanceID'], 
                                  options.pipeline)

# documentation: https://fnndsc.github.io/chris_plugin/
@chris_plugin(
    parser              = parser,
    title               = 'Dynamic Pipeline/plugin generator',
    category            = 'Topological',        # ref. https://chrisstore.co/plugins
    min_memory_limit    = '100Mi',              # supported units: Mi, Gi
    min_cpu_limit       = '1000m',              # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit       = 0                     # set min_gpu_limit=1 to enable GPU
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    global Env, PLinputFilter, CAW
    # pudb.set_trace()
    if len(options.pluginInstanceID):
        Env.parentPluginInstanceID    = options.pluginInstanceID
    else:
        Env.parentPluginInstanceID_discover()
    if len(Env.parentPluginInstanceID):
        # are we branching off dirs or files?
        if options.dirsOnly:
            mapper  = PathMapper(inputdir, outputdir, glob=options.pattern, only_files = False)
        else:
            mapper = PathMapper(inputdir, outputdir, glob=options.pattern)

        for input, output in mapper:
            tree_grow(options, input, output)


if __name__ == '__main__':
    main()
