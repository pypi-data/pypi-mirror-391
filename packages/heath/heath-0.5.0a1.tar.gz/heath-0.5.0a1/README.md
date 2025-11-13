# Heath — Manage projections

Heath is a CLI to manage projection ledger and a library to make it easy
for any project working with events and projections to integrate those features.

Define the DSN to work with:

```console
$ export HEATH_DSN="sqlite:////tmp/projections.sqlite"
```

Initialise projection database:

```console
$ heath init
```

List the projections:

```console
$ heath status
```
