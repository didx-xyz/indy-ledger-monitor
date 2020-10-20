# Indy Ledger Monitor

Indy Ledger Monitor is a set of tools for fetching transactions from an Indy Ledger by querying the validators of the ledger. Based on that, requests can be made for ledger transactions such as:

* fetch pool ledger transactions
* fetch main ledger transaction(s)
* fetch schema id details
* fetch credential definition details
* fetch revocation details

The repo has basic tools to collect and format data and tools for using that data in different ways.

## Fetch Ledger Information

This is a simple tool that can be used to retrieve ledger transactions from an Indy network. The results are returned as a JSON.

For more details see the Fetch Ledger Information [readme](fetch-ledger-tx/README.md)

## Contributions

Pull requests are welcome! Please read our [contributions guide](CONTRIBUTING.md) and submit your PRs. We enforce developer certificate of origin (DCO) commit signing. See guidance [here](https://github.com/apps/dco).

We also welcome issues submitted about problems you encounter in using the tools within this repo.

## Code of Conduct

All contributors are required to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) guidelines.

## License

[Apache License Version 2.0](LICENSE)