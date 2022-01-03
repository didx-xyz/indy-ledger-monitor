# Plug-ins

## Building Plug-ins

Build your own class based plugins to extract the information you want. Have a look at the included [example plug-in](Example/example.py) to see how to build your own. 

## About Plug-ins

Plug-in modals and packages are collected from the plug-ins folder and sorted based on the order specified by you by setting the index property in the given plug-in. Once the plug-ins are loaded the command line arguments are collected from the `parse_args()` function from each of the plug-ins. They are then passed into the `load_parse_args()` function where the plug-in collects its class variables.

Once the plug-ins are initialized, the monitor engine will connect to the pool of the specified network. The engine will then pass the pool connection to the plug-ins to allow them to collect and manipulate the data.

The data collected from the network is passed in sequence to each of the plugins, giving each the opportunity to parse and manipulate the data before passing the result back for subsequent plugins. 

*Note that this works slightly different from [indy-node-monitor](https://github.com/hyperledger/indy-node-monitor). Data is appended to the results by each plug-in. So a result needs to be created by a plug-in first then data can be manipulated or appended too.* 

*Note: plug-ins are only enabled when a flag is given. i.e. the [example plug-in](Example/example.py) will only run if the `--example` flag is given. If you have a plug-in that requires more then one argument the first flag will enable the plug-in and the following flags would contain your additional arguments. See the [readme](metrics/README.md) as an example*

Have a look at the included plug-ins to get an idea of how to build your own!

### How To Use
`./run.sh --net ssn --maintx (Positive Integer)` or `./run.sh --net ssn --maintxr (Positive Integer)-(Positive Integer)`

## Plug-ins

### credid
The [credid Plug-in](credid.py) gets a specific schema from the ledger. (TxnID of CLAIM_DEF).

### maintx
The [maintx Plug-in](maintx.py) gets a specific transaction number from main ledger.

### maintxr
The [maintxr Plug-in](maintxr.py) gets a range of transactions from main ledger.

### pooltx
The [pooltx Plug-in](pooltx.py) gets pool ledger transactions.

### schemaid
The [schemaid Plug-in](schemaid.py) gets a specific schema from ledger. (TxnID of SCHEMA).

### Example
See [readme](Example/README.md).

### Metrics
See [readme](metrics/README.md).
