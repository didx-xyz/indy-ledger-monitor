# This example shows the basic structure required in order for a plugin to be run.

# Reqired
import plugin_collection

# Add your imports here
import json

# The plug-in collection will find any base classes in the file.
class main(plugin_collection.Plugin):
    # __init__ is required and has the necessary items in order to differentiate between plug-ins
    def __init__(self, example: bool = False):
        # Below is required in order to diferecate between plug-ins 
        super().__init__()
        self.index = -1 # Set to -1 to disable plug-in.
        self.name = 'Example Plug-in'
        self.description = ''
        self.type = ''

        # Decleare your parser varaibles here
        # These are used to get info from the parser on whether to run your plug-in, arguments, etc.
        # Remember to declare the empty inside the function declaration i.e. status_only: bool = False
        self.example = example

    # Declear your parser arguments here. This will get them and add them to the fetch_status.py parser arguments
    # and allow them to come up in the help flag.
    def parse_args(self, parser, argv=None):
        parser.add_argument("--example", action="store_true", help="Runs expample plug-in")

    # Here you set your variables with the arguments from the parser
    def load_parse_args(self, args):
        # Important for maintaining global verbose
        global verbose
        verbose = args.verbose
        
        # Set your varables here
        self.example = args.example
    
    # The is where your main code goes and what is kicked off after the information has been gotten from the pool
    # and gets passed the results of the network and the name of the network the results came from and the pool.
    async def perform_operation(self, result, pool, network_name):
        # This is required to see whether the plug-in was asked to be run by the user.
        if self.example:

            # Main code here
            print("Example plug-in has run.")