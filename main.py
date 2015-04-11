import nsb_config
import os.path
from pprint import pprint

def read_options():
    #Will exit here if --help is supplied
    cl_options = nsb_config.get_command_line_args()

    debug = 'debug' in cl_options
    if debug:
        pprint(sorted(cl_options.items()))


    global_path = nsb_config.default_global_path
    global_options = nsb_config.get_global_options(global_path)

    user_path = cl_options.get('config') or global_options['config']
    
    user_path = nsb_config.evaluate_path(user_path)
    
    #We tolerate missing file if 'config' is not supplied
    #at the command line
    user_options = nsb_config.get_user_options(user_path,
            'config' not in cl_options)
    
    options = global_options.copy()
    options.update(user_options)
    options.update(cl_options)

    return options

def main():
    options = read_options()




if __name__ == '__main__':
    main()
