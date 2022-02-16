str_about = '''
    This module is responsible for handling some state related information
    which is mostly information about the ChRIS/CUBE instance.

    Core data includes information on the ChRIS/CUBE instances as well as
    information relevant to the pipeline to be scheduled.
'''

class CUBEinstance:
    '''
    A class that contains data pertinent to a specific CUBE instance
    '''

    def __init__(self, *args, **kwargs):
        self.d_CUBE = {
            'username'  : 'chris',
            'password'  : 'chris1234',
            'IP'        : 'localhost',
            'port'      : ':8000',
            'route'     : '/api/v1/',
            'protocol'  : 'http:',
            'url'       : ''
        }

    def url(self, *args):
        '''
        get/set the URL
        '''
        if len(args):
            self.d_CUBE['url']  = args[0]
        else:
            self.d_CUBE['url']  = '%s%s%s%s' % (
                self.d_CUBE['protocol'],
                self.d_CUBE['IP'],
                self.d_CUBE['port'],
                self.d_CUBE['route']
            )

    def set(self, str_key, str_val):
        '''
        set str_key to str_val
        '''
        if str_key in self.d_CUBE.keys():
            self.d_CUBE[str_key]    = str_val

    def __call__(self, str_key):
        '''
        get a value for a str_key
        '''
        if str_key in self.d_CUBE.keys():
            return self.d_CUBE[str_key]
        else:
            return ''

class Pipeline:
    '''
    Information pertinent to the pipline being scheduled. This is
    encapsulated with a class object to allow for possible future
    expansion.
    '''

    def __init__(self, *args, **kwargs):

        self.str_pipelineName       = ''

        