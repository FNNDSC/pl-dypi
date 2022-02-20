#!/usr/bin/env python

from    distutils.log           import Log
from    multiprocessing.spawn   import import_main_path
from    pathlib                 import Path
from    argparse                import ArgumentParser, Namespace
from    chris_plugin            import chris_plugin, PathMapper
from    loguru                  import logger
from    pathlib                 import Path

import  os
import  pudb

from    state                   import data
from    logic                   import behavior
from    control                 import action

import  pfmisc
from    pfmisc._colors          import Colors

Env             = data.CUBEinstance()
PLinputFilter   = action.PluginRun(env = Env)
CAW             = action.Caw(env = Env)
PFMlogger       = None
LOG             = None

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
parser.add_argument(
            '-v', '--verbosity',
            default = '0',
            help    = 'verbosity level of app'
)

def inputdir_listFiles(input: Path):
    '''
    List the files in Path -- mostly for debugging
    '''
    global LOG

    LOG("Listing files in %s" % str(input))
    # read the entries
    with os.scandir(str(input)) as listOfEntries:
        for entry in listOfEntries:
            # print all entries that are files
            if entry.is_file():
                LOG(entry.name)

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
    global Env, PLinputFilter, CAW, LOG

    conditional             = behavior.Filter()
    conditional.obj_pass    = unconditionalPass

    if conditional.obj_pass(str(input)):
        d_nodeInput         = PLinputFilter(str(input))
        if d_nodeInput['status']:
            if len(options.pipeline):
                d_caw           = CAW(d_nodeInput['branchInstanceID'], 
                                    options.pipeline)
        else:
            LOG("Some error was returned from the node analysis!",  comms = 'error')
            LOG('stdout: %s' % d_nodeInput['run']['stdout'],        comms = 'error')
            LOG('stderr: %s' % d_nodeInput['run']['stderr'],        comms = 'error')
            LOG('return: %s' % d_nodeInput['run']['returncode'],    comms = 'error')

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
    global Env, PLinputFilter, CAW, PFMlogger, LOG
    PFMlogger           =  pfmisc.debug(
                                        verbosity   = int(options.verbosity),
                                        within      = 'main',
                                        syslog      = True
                                        )     
    LOG                 = PFMlogger.qprint

    LOG("Starting application...")
    for k,v in options.__dict__.items():
         LOG("%25s:  [%s]" % (k, v))
    LOG("")
    LOG("inputdir  = %s" % str(inputdir))        
    LOG("outputdir = %s" % str(outputdir))        
    inputdir_listFiles(inputdir)

    if len(options.pluginInstanceID):
        Env.parentPluginInstanceID    = options.pluginInstanceID
    else:
        Env.parentPluginInstanceID_discover()
    if len(Env.parentPluginInstanceID):
        # are we branching off dirs or files?
        if options.dirsOnly:
            mapper = PathMapper(inputdir, outputdir, glob=options.pattern, only_files = False)
        else:
            mapper = PathMapper(inputdir, outputdir, glob=options.pattern)

        LOG("Processing mapper...")
        Path('%s/start.touch' % str(outputdir)).touch()

        for input, output in mapper:
            LOG("Growing a tree off new data root %s" % str(input))
            tree_grow(options, input, output)

    LOG("Application terminating...")

if __name__ == '__main__':
    main()
