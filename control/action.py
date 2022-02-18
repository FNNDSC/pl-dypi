str_about = '''
    The action module provides functionality to run individual
    plugins as well as "pipelines" of plugins. It is the interface
    between the plugin and a CUBE API via the CLI.
'''

import  subprocess
import  os
import  re
import  pudb
import  json

class jobber:

    def __init__(self, d_args : dict):
        """Constructor for the jobber class.

        Args:
            d_args (dict): a dictionary of "arguments" (parameters) for the
                           object.
        """
        self.args   = d_args.copy()
        if not 'verbosity'      in self.args.keys(): self.args['verbosity']     = 0
        if not 'noJobLogging'   in self.args.keys(): self.args['noJobLogging']  = False

    def dict2JSONcli(self, d_dict : dict) -> str:
        """Convert a dictionary into a CLI conformant JSON string.

        An input dictionary of

            {
                'key1': 'value1',
                'key2': 'value2'
            }

        is converted to a string:

            "{\"key1\":\"value1\",\"key2\":\"value2\"}"

        Args:
            d_dict (dict): a python dictionary to convert

        Returns:
            str: CLI equivalent string.
        """

        str_JSON    = json.dumps(d_dict)
        str_JSON    = str_JSON.replace('"', r'\"')
        return str_JSON

    def dict2cli(self, d_dict : dict) -> str:
        """Convert a dictionary into a CLI conformant JSON string.

        An input dictionary of

            {
                'key1': 'value1',
                'key2': 'value2',
                'key3': true,
                'key4': false
            }

        is converted to a string:

            "--key1 value1 --key2 value2 --key3"

        Args:
            d_dict (dict): a python dictionary to convert

        Returns:
            str: CLI equivalent string.
        """
        str_cli     : str = ""
        for k,v in d_dict.items():
            if type(v) == bool:
                if v:
                    str_cli += '--%s ' % k
            elif len(v):
                str_cli += '--%s %s ' % (k, v)
        return str_cli

    def job_run(self, str_cmd):
        """
        Running some CLI process via python is cumbersome. The typical/easy
        path of
                            os.system(str_cmd)
        is deprecated and prone to hidden complexity. The preferred
        method is via subprocess, which has a cumbersome processing
        syntax. Still, this method runs the `str_cmd` and returns the
        stderr and stdout strings as well as a returncode.
        Providing readtime output of both stdout and stderr seems
        problematic. The approach here is to provide realtime
        output on stdout and only provide stderr on process completion.
        """
        d_ret       : dict = {
            'stdout':       "",
            'stderr':       "",
            'cmd':          "",
            'cwd':          "",
            'returncode':   0
        }
        str_stdoutLine  : str   = ""
        str_stdout      : str   = ""

        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
        )

        # Realtime output on stdout
        while True:
            stdout      = p.stdout.readline()
            if p.poll() is not None:
                break
            if stdout:
                str_stdoutLine = stdout.decode()
                if int(self.args['verbosity']):
                    print(str_stdoutLine, end = '')
                str_stdout      += str_stdoutLine
        d_ret['cmd']        = str_cmd
        d_ret['cwd']        = os.getcwd()
        d_ret['stdout']     = str_stdout
        d_ret['stderr']     = p.stderr.read().decode()
        d_ret['returncode'] = p.returncode
        with open('/tmp/job.json', 'w') as f:
            json.dump(d_ret, f, indent=4)
        if int(self.args['verbosity']) and len(d_ret['stderr']):
            print('\nstderr: \n%s' % d_ret['stderr'])
        return d_ret

    def job_runbg(self, str_cmd : str) -> dict:
        """Run a job in the background

        Args:
            str_cmd (str): CLI string to run

        Returns:
            dict: a dictionary of exec state
        """
        d_ret       : dict = {
            'uid'       : "",
            'cmd'       : "",
            'cwd'       : ""
        }
        # str_stdoutLine  : str   = ""
        # str_stdout      : str   = ""

        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
        )

        d_ret['uid']        = str(os.getuid())
        d_ret['cmd']        = str_cmd
        d_ret['cwd']        = os.getcwd()
        # d_ret['stdout']     = str_stdout
        # d_ret['stderr']     = p.stderr.read().decode()
        # d_ret['returncode'] = p.returncode
        # if int(self.args['verbosity']) and len(d_ret['stderr']):
        #     print('\nstderr: \n%s' % d_ret['stderr'])
        return d_ret

    def job_stdwrite(self, d_job, str_outputDir, str_prefix = ""):
        """
        Capture the d_job entries to respective files.
        """
        if not self.args['noJobLogging']:
            for key in d_job.keys():
                with open(
                    '%s/%s%s' % (str_outputDir, str_prefix, key), "w"
                ) as f:
                    f.write(str(d_job[key]))
                    f.close()
        return {
            'status': True
        }

class PluginRun:
    '''
    A class wrapper about the CLI tool "chrispl-run" that POSTs a pl-pfdorun
    to CUBE.
    '''
    def __init__(self, *args, **kwargs):
        self.env                = None
        self.plugin             = ''
        self.shell              : jobber    = jobber({'verbosity' : 1, 'noJobLogging': True})
        self.attachToPluginID   : str       = ''
        for k, v in kwargs.items():
            if k == 'attachToPluginID'  :   self.attachToPluginID   = v
            if k == 'env'               :   self.env                = v

        self.l_runCMDresp       : list  = []
        self.l_branchInstanceID : list  = []

    def PLpfdorun_args(self, str_input : str) -> dict:
        '''
        Return the argument string pertinent to the pl-pfdorun plugin
        '''
        str_args : str = """
            --fileFilter=%s;
            --exec='cp %%inputWorkingDir/%%inputWorkingFile %%outputWorkingDir/%%inputWorkingFile';
            --noJobLogging;
            --verbose=5;
            --title=%s;
            --previous_id=%s
        """ % (str_input, str_input, self.env.parentPluginInstanceID)
        str_args = re.sub(r';\n.*--', ';--', str_args) 
        str_args = str_args.strip()
        return {
            'args':     str_args
        }

    def chrispl_onCUBEargs(self):
        '''
        Return a string specifying the CUBE instance
        '''
        return {
            'onCUBE':  json.dumps(self.env.onCUBE())
        }

    def chrispl_run_cmd(self, str_inputData : str) -> dict:
        '''
        Return the CLI for the chrispl_run
        '''
        str_cmd = """chrispl-run --plugin name=pl-pfdorun --args="%s" --onCUBE %s""" % (
                self.PLpfdorun_args(str_inputData)['args'],
                json.dumps(self.chrispl_onCUBEargs()['onCUBE'], indent = 4)
            )
        str_cmd = str_cmd.strip().replace('\n', '')
        return {
            'cmd' : str_cmd
        }

    def __call__(self, str_input : str) ->dict:
        '''
        Copy the <str_input> to the output using pl-pfdorun
        '''
        # Remove the '/incoming/' from the str_input
        str_inputTarget     : str   = str_input.split('/')[2]
        d_PLCmd             : dict  = self.chrispl_run_cmd(str_inputTarget)
        str_PLCmd           : str   = d_PLCmd['cmd'] 
        str_PLCmdfile       : str   = '/tmp/%s.sh' % str_inputTarget

        with open(str_PLCmdfile, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write(str_PLCmd)
        os.chmod(str_PLCmdfile, 0o755)
        d_runCMDresp        : dict  = self.shell.job_run(str_PLCmdfile)
        if not d_runCMDresp['returncode']:
            self.l_runCMDresp.append(d_runCMDresp)
            branchID        : int   = d_runCMDresp['stdout'].split()[2]
            self.l_branchInstanceID.append(branchID)

        return {
            'branchInstanceID': branchID
        }

class Caw:
    '''
    A class wrapper about the CLI tool "caw" that can POST a pipeline to
    a plugin instance ID
    '''

    def __init__(self, *args, **kwargs):
        self.env                = None
        self.pipeline           : str       = ''
        self.shell              : jobber    =  jobber({'verbosity' : 1, 'noJobLogging': True})
        self.attachToPluginID   : str       = ''
        for k, v in kwargs.items():
            if k == 'attachToPluginID'  :   self.attachToPluginID   = v
            if k == 'env'               :   self.env                = v
        self.l_runCMDresp       : list  = []

    def pipeline(self, *args) -> str:
        '''
        pipeline name get/set
        '''
        if len(args):
            self.pipeline   = args[0]
        return self.pipeline

    def caw_argsCore(self) -> dict:
        '''
        Return the argument string pertinent to the caw
        '''
        str_args : str = """
            --address %s --username %s --password %s
        """ % (
            self.env.url(), self.env('user'), self.env('password')
        )
        return {
            'args': str_args
        }

    def caw_run_cmd(self, attachToPluginID: int, pipeline: str) -> dict:
        '''
        Return the CLI for the caw call
        '''
        str_cmd = """caw %s pipeline --target %s "%s" """ % (
            self.caw_argsCore()['args'], attachToPluginID, pipeline
        )
        str_cmd = str_cmd.strip().replace('\n', '')
        return {
            'cmd' : str_cmd
        }

    def __call__(self, filteredCopyInstanceID : dict, str_pipeline : str) -> dict:
        '''
        Call caw on the appropriate plugin instance ID
        '''
        d_cawCmd            : dict  = self.caw_run_cmd(filteredCopyInstanceID, str_pipeline)
        str_cawCmd          : str   = d_cawCmd['cmd'] 
        str_cawCmdfile      : str   = '/tmp/caw-%s.sh' % filteredCopyInstanceID

        with open(str_cawCmdfile, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write(str_cawCmd)
        os.chmod(str_cawCmdfile, 0o755)
        d_runCMDresp        : dict  = self.shell.job_run(str_cawCmdfile)
        return {
            'response'      : d_runCMDresp
        }
       