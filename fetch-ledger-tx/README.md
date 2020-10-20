# Fetch Ledger Transactions

This folder contains a simple Python script that uses [indy-vdr](https://github.com/hyperledger/indy-vdr) to execute various calls to an Indy network to fetch ledger transactions. 

The various transaction parameters returns a information such as schema_id lookups, cred_def_id lookups, pool ledger transaction or main ledger transactions about the accessed ledger. 

An example of the JSON data returned by the call for an individual node is provided [below](#example-validator-info).

No authourised DID is required and this tool can always be run with the -a parameter so that it run in anonymous mode.

The easiest way to use this now is to use the `./run` script and the Docker build process provide in this folder. Work is in progress to add a CI/CD capability to `indy-vdr` so that the artifacts are published to PyPi and native Python apps can be used. In the meantime, we recommend either making changes to the included Python script, or better, just adding programs that read from standard input and process the output of the `./run` script.

## How To Run

Here is guidance of how you can run the script to get ledger transaction information about any accessible Indy network. We'll start with a test on local network (using [von-network](https://github.com/bcgov/von-network)) and provide how this can be run on any Indy network, including Sovrin networks.

### Prerequisites

If you are running locally, you must have `git`, `docker` and a bash terminal. On Windows, when you install `git`, the `git-bash` terminal is installed and you can use that.

To try this in a browser, go to [Play With Docker](https://labs.play-with-docker.com/), login (requires a Docker Hub ID) and click the "+ ADD NEW INSTANCE` link (left side). That opens a terminal session that you can use to run these steps.

The rest of the steps assume you are in your bash terminal in a folder where GitHub repos can be cloned.

### Start VON Network

To start a local Indy network to test with, we'll clone a VON Network, build it and start it using the following commands run in a bash terminal:

``` bash
git clone https://github.com/bcgov/von-network
cd von-network
./manage build
./manage start
cd ..

```

The build step will take a while as 1/3 of the Internet is downloaded. Eventually, the `start` step will execute and a four-node Indy ledger will start.  Wait about 30 seconds and then go to the web interface to view the network.

- If you are running locally, go to [http://localhost:9000](http://localhost:9000).
- If you are on Play with Docker, click the `9000` link above the terminal session window.

Note the last command above puts you back up to the folder in which you started. If you want to explore `von-network` you'll have to change back into the `von-network` folder.

When you are finished your running the validator tool (covered in the steps below) and want to stop your local indy-network, change to the von-network folder and run:

```bash
./manage down

```

We'll remind you of that later in these instructions.

### Clone the indy-ledger-monitor repo

Run these commands to clone this repo so that you can run the fetch validator info command.

```bash
git clone https://github.com/didx-xyz/indy-ledger-monitor
cd indy-ledger-monitor/fetch-ledger-tx

```

### Run the Ledger Info Script

For a full list of script options run:
``` bash
./run.sh -h
```

To get the details for the known networks available for use with the `--net` option, run:
``` bash
./run.sh --list-nets
```

To run the ledger info script, run the following command in your bash terminal from the `fetch-ledger-tx` folder in the `indy-ledger-monitor` clone:

``` bash
./run.sh -a --net=<netId> --seed=<SEED>
```
or
``` bash
./run.sh -a --genesis-url=<URL> --seed=<SEED>
```

This repo don't require any privileged DID and the `-a` parameter can be used at all times.
``` bash
./run.sh --net=<netId> -a
```
or
``` bash
./run.sh --genesis-url=<URL> -a
```

To fetch pool transactions, run:
``` bash
./run.sh -a --net=<netId> --pooltx
```
or
``` bash
./run.sh -a --genesis-url=<URL> --pooltx
```

To fetch a specific main ledger transaction use the `--maintx` argument and provide a transaction sequence number;
``` bash
./run.sh -a --net=<netId> --maintx 1
```

To fetch a range of main ledger transactions use the `--maintxr` argument and provide a transaction sequence number range;
``` bash
./run.sh -a --net=<netId> --maintx 1-5
```

To fetch a schema id from the ledger use the `--schemaid` argument and provide a schema id;
``` bash
./run.sh -a --net=<netId> --schemaid QXdMLmAKZmQBhnvXHxKn78:2:SURFNetSchema:1.0
```

To fetch a credential definition id of main ledger transactions use the `--credid` argument and provide a transaction credential definition id;
``` bash
./run.sh -a --net=<netId> --credid A9Rsuu7FNquw8Ne2Smu5Nr:3:CL:15:tag
```

For the first test run using von-network:

- the `<SEED>` is the Indy test network Trustee seed: `000000000000000000000000Trustee1`.
- the URL is retrieved by clicking on the `Genesis Transaction` link in the VON-Network web interface and copying the URL from the browser address bar.

If you are running locally, the full command is:

``` bash
./run.sh --net=vn --seed=000000000000000000000000Trustee1 --pooltx
```
or
``` bash
./run.sh --genesis-url=http://localhost:9000/genesis --seed=000000000000000000000000Trustee1 --pooltx
```

If running in the browser, you will have to get the URL for the Genesis file (as described above) and replace the `localhost` URL above.

You should see a very long JSON structure printed to the terminal. You can redirect the output to a file by adding something like `> pool_transactions.json` at the end of the command.

### Running against other Indy Networks

To see the ledger info script against any other Indy network, you need a URL for the Genesis file for the network, and the seed for a suitably authorized DID. The pool Genesis file URLs are easy, since that is published data needed by agents connecting to Indy networks. Sovrin genesis URLs can be found [here](https://github.com/sovrin-foundation/sovrin/tree/master/sovrin). You need the URL for the raw version of the pool transaction files. For example, the URL you need for the Sovrin MainNet is:

- [`https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_live_genesis`](`https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_live_genesis`)

For the other Sovrin networks, replace `live` with `sandbox` (Sovrin Staging Net) and `builder` (Sovrin Builder Net).

Getting a Seed for a DID with sufficient authorization on specific ledger is an exercise for the user. **DO NOT SHARE DID SEEDS**. Those are to be kept secret.

Do not write the Seeds in a public form. The use of environment variables for these parameters is very deliberate so that no one accidentally leaks an authorized DID.

Did I mention: **DO NOT SHARE DID SEEDS**?

## Example ledger info for a specific ledger transaction

The following is an example of the data for a single ledger transaction from Sovrin Mainnet:

` ./run.sh -a --net=smn --maintx 1`

```JSONC
{
  "reqId": 1603231860162518000,
  "state_proof": {
    "multi_signature": {
      "participants": [
        "royal_sovrin",
        "sovrin.sicpa.com",
        "OASFCU",
        "findentity",
        "ServerVS",
        "danube",
        "atbsovrin",
        "pcValidator01",
        "Stuard",
        "DustStorm",
        "prosovitor",
        "VeridiumIDC",
        "BIGAWSUSEAST1-001"
      ],
      "value": {
        "txn_root_hash": "HTCnwnhv2ES1DCNeHxMJD7HhxVLWCSUszPGBMXiHpoJr",
        "ledger_id": 1,
        "state_root_hash": "5Gqwywact5rWiNGNTr3XjkvzebtQV7AM2EyMcjSBpNd5",
        "timestamp": 1603231818,
        "pool_state_root_hash": "4Asf2cSvxUguXoSsxHxbKSmgXHiaNgWWYR5uLj35BiuA"
      },
      "signature": "RD4s4FhUpCbcXYKUduHnd6CM79EEJ4RCrKpPFioYMyHMKLB5vX3zWv2Yy28BuAtcMEuLmCUNJBrUhVxF1hWFoP7KTunSDeViqyWuiWrVMpwZUymGsYR2bZ1aAJSrD31Zr5LGW1XGoHNqJH8RsCmpVQmrWcHXxmHRUpk2xRU9goigFq"
    }
  },
  "type": "3",
  "seqNo": 1,
  "identifier": "LibindyDid111111111111",
  "data": {
    "txnMetadata": {
      "seqNo": 1
    },
    "ver": "1",
    "rootHash": "HTCnwnhv2ES1DCNeHxMJD7HhxVLWCSUszPGBMXiHpoJr",
    "txn": {
      "metadata": {},
      "type": "1",
      "data": {
        "dest": "NMjQb59rKTJXKNqVYfcZFi",
        "role": "0",
        "verkey": "Ce9jZ2bQcLRCrY3eT5AbjsU5mXFa4jMF6dDSF21tyeFJ",
        "alias": "Phil Windley"
      }
    },
    "auditPath": [
      "6rwuBfxhqdByev94TgaXrC3TyDYnPvoChi86in3tj1gc",
      "WxtLaCqWq36hcqozYp5WFJGmCPtUh1nuSU3tkB5RZmq",
      "XtbhzTr7upNXsJUkEiciogpGpu1wu9ARLgNEuotkwWM",
      "2gCD8YRUUMVZyJ7TLXT4qbCxw1h1hijX8koaLDFc1bJq",
      "BuvAvcc92Tgwu6PUFMZY21WM3dg5KD1fhfFHkdgGfGWJ",
      "6xzkXYsfhy2LRBpkwb4n2zJwrgNrDTQKvnk4oP8e9jvM",
      "EAbTZdeMabd5aW59CbyhQ1q7MRpHXMFVzcJFQSz6yCV3",
      "94F6q15MhEhQeijZuA1zerM2oefBbUiifdzdbcQ7hKPN",
      "4bmnnZRY1RtMhdLcEcKy5FccPdt27iH45PiVAuoBMwsj",
      "3fdwTL8jHHQYfzNrtmZ4yLzGNEUC65hwMSVT86Uf7PQh",
      "8UpRMwf1YwhqZUVARivJwkSFqe91ft4jipgo8Z1Xaeh4",
      "BQPTuYEpmnZQ6GdjBAzHBGJVzkpWnfNMNGNpyJ8LAQZ",
      "G8L5Sz9pPT351NkVvYWV6kcwR1ycwEAsk5pQZApTPbsA",
      "4jGpg6VrrSKmZrwQozupNCEkpmsMdekGt4SkAzuHmqHP",
      "CCuh1YQexAhFwvVagcGc7knXUoinjz4hShneqMacvhN3",
      "6zJcFtbCmMNRyQiYtUyTZM4y1aK4MwGHQKf67QfckEgX"
    ],
    "reqSignature": {},
    "ledgerSize": 55766
  }
}
```
