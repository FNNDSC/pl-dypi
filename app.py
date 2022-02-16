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

parser = ArgumentParser(description='ChRIS DS plugin that creates responsive/dynamic compute trees.')
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
            help    = 'plugin instance ID containing data space on which to dynamically build'
)


def unconditionalPass(str_object: str) -> bool:
    '''
    If a more complex conditional is required, code it here.
    '''
    return True

def tree_grow(input: Path, output: Path, env: data) -> dict:
    '''
    Based on some conditional of the <input> direct the
    dynamic "growth" of this feed tree from the parent node
    of *this* plugin.
    '''
    conditional             = behavior.Filter()
    conditional.obj_pass    = unconditionalPass
    dircopy                 = action.PluginRun(env = env)
    caw                     = action.Caw()

    if conditional.obj_pass(str(input)):
        d_copy          = dircopy(str(input))
        d_caw           = caw(d_copy)

# documentation: https://fnndsc.github.io/chris_plugin/
@chris_plugin(
    parser              = parser,
    title               = 'Dynamic Pipeline/plugin generator',
    category            = '',                   # ref. https://chrisstore.co/plugins
    min_memory_limit    = '100Mi',              # supported units: Mi, Gi
    min_cpu_limit       = '1000m',              # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit       = 0                     # set min_gpu_limit=1 to enable GPU
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    pudb.set_trace()

    Env                     = data.CUBEinstance()
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
            tree_grow(input, output, Env)


if __name__ == '__main__':
    main()
