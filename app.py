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
            type    = bool,
            action  = 'store_true' 
            default = False,
            help    = 'if specified, only filter directories, not files'
)
parser.add_argument(
            'p', '--pipeline',
            default = '',
            help    = 'pipeline string to execute on filtered child node'
)

def unconditionalPass(str_object: str) -> bool:
    '''
    If a more complex conditional is required, code it here.
    '''
    return True

def tree_dynamicBuild(input: Path, output: Path) -> dict:
    '''
    Based on some evaluation of the <input> execute some
    specific behaviour
    '''
    conditional             = behavior.Filter()
    conditional.obj_pass    = unconditionalPass
    dircopy                 = action.PluginRun()
    caw                     = action.Caw()

    if conditional.obj_pass(str(input)):
        d_copy          = dircopy(str(input))
        d_caw           = caw(d_copy)

# documentation: https://fnndsc.github.io/chris_plugin/
@chris_plugin(
    parser              = parser,
    title               = 'My ChRIS plugin',
    category            = '',                   # ref. https://chrisstore.co/plugins
    min_memory_limit    = '100Mi',              # supported units: Mi, Gi
    min_cpu_limit       = '1000m',              # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit       = 0                     # set min_gpu_limit=1 to enable GPU
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    pudb.set_trace()

    if options.dirsOnly:
        mapper  = PathMapper(inputdir, outputdir, glob=options.pattern, only_files = False)
    else:
        mapper = PathMapper(inputdir, outputdir, glob=options.pattern)
    for input, output in mapper:
        tree_dynamicBuild(input, output)


if __name__ == '__main__':
    main()
