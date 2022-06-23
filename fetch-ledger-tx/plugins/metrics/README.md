# Network Metrics

The [Network Metrics Plug-in](sovrin_network_metrics.py) is used to create the Adoption & Usage graphs for the [metric dashboard](https://sovrin.org/ssi-metrics-dashboards/) on the [sovrin website](https://sovrin.org/) and could be used to log any other data to google sheets. This will append rows inside google sheets allowing you to log and create graphs off the monitor. Pair this with a cron job to run every so often and you have your own transaction logs.

## Setup
In order to use the Network Metrics Plug-in your self you will need to create a folder named "conf" in the network metrics folder. That folder will need to have a google api credentials json file in it. Follow this [tutorial](https://www.youtube.com/watch?v=cnPlKLEGR7E&t=33s) on how to create the json file and how to set it up in google sheets. Make sure you watch the video to 3m 56s in order to set things up fully.

Your metrics plug-in should look something like this:

metrics\
----> conf\
--------> *GoogleAPI.json (Name it what ever you want)*\
----> google_sheets.py\
----> README.md\
----> sovrin_network_metrics.py

## How To Use
Important: In order for this to work you must create another worksheet called `metaData` with the following.

|   | A        | B                                          |
|---|----------|--------------------------------------------|
| 1 | Sheet ID |                        Max Last Logged Txn |
| 2 |        0 |         =MAX(SORT([Worksheet name]!A$2:A)) |

Once that is set up, the plug-in the command should look something like this:\
`./run.sh --net ssn -v --mlog --json [Json File Name] --fileid [Google Sheet id*] --worksheet [Worksheet name]`
* Can be found in the sheet URL after /d/

CSV Option:\
`IM=1 ./run.sh --net ssn --mlog --batchsize 30 --csv [Transaction SeqNo] -v`
* Must create a log file in the root directory call `logs`

--mlog: enables the plug-in\
--json: The google API json file you would like to use inside the conf folder.\
--fileid: The google sheet you would like to work with.\
--worksheet: The worksheet you would like to work with, in the given google sheet file.
--batchsize: Specify the read/write batch size. Not Required. Default is 10.

And your done!

