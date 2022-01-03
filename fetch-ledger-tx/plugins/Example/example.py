# This example shows the basic structure required in order for a plugin to be run.

# Reqired
import plugin_collection

# Add your imports here
from util import log

# The plug-in collection parent class will find classes in the file.
class main(plugin_collection.Plugin):
    # __init__ is required and has the necessary items in order to differentiate between plug-ins.
    def __init__(self):
        super().__init__()
        self.index = 3
        self.name = 'Example Plug-in'
        self.description = ''
        self.type = ''

    # Declear your parser arguments here. This will add them to the main.py parser arguments.
    def parse_args(self, parser):
        parser.add_argument("--example", action="store_true", help="Runs expample plug-in")

    # Here you set your variables with the arguments from the parser
    def load_parse_args(self, args):
        # Important for maintaining global verbose
        global verbose
        verbose = args.verbose
        
        # Required to enable your plug-in. This should match your parser argument. i.e. --example -> args.example
        self.enabled = args.example

        # Set your varables here
    
    # This is where your main code goes and what is kicked off after the information has been gotten from the network.
    # This is passed the results from the network and the name of the network.
    async def perform_operation(self, pool, result, network_name):
        # Main code here
        ExStr = "Example plug-in has run."

        # append data to result
        result = result + [ExStr]

        # Required for chaining plugins whether or not you are using result.
        return result