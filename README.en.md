# voicebench-load

A provider-neutral load testing toolkit for speech and voice model APIs.

The project focuses on repeatable audio fixtures, async load profiles, and readable reports for authorized systems.


## Quick start

```bash
python -m pip install -e ".[dev]"
voicebench-load run examples/generic-json-base64.yaml
```

Use environment variables for credentials. Only load test systems you own or are authorized to test.
