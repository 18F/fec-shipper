# fec-shipper

This repository holds a set of scripts for importing legal data into openFEC api.

# Running

To load regs, run

```bash
$ python regulations.py env
```
Where env can be local, feature, stage or prod.

Note: When regulations need to be removed, the best way to do that is to drop the
elastic search instance and re-add it, by doing:

```bash
$ cf unbind fec-search-prod api
$ cf delete-service fec-search-prod
$ cf create-service elasticsearch-swarm-1.7.1 1x fec-search-prod
$ cf restage api
```

## Public domain
This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
