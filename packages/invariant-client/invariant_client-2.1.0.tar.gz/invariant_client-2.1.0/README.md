# Invariant CLI and Python SDK

## Installation

The Invariant client is available as a Python package. You can install it through pip or pipx like so:

```bash
pip install invariant-client

# Or using pipx
pipx install invariant-client
```

The Invariant CLI can be used to run Invariant from your test automation workflow. This example shows one way to install it for Github Actions:

```yaml
steps:
- uses: actions/checkout@v4
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'
- name: Install dependencies
  run: python -m pip install --upgrade pip invariant-client
- name: Evaluate current directory using Invariant
  run: |
    python -m invariant-client run
```

## Usage: Command Line Interface

The Invariant CLI can analyize local changes to network configuration files.

```bash
$ invariant login
Open this link in your browser to log in:
https://prod.invariant.tech/login?code=320664
Login successful.

$ invariant run
Uploading snapshot...
Processing... (5b7f28b5-95b3-44ee-8c42-ea0240ef52f5)
Analysis complete.

╭───────────────────────┬────────╮
│ Network Information   │   Rows │
├───────────────────────┼────────┤
│ nodes                 │     38 │
│ interfaces            │    201 │
│ named_structures      │    148 │
│ defined_structures    │    334 │
│ referenced_structures │    333 │
│ unused_structures     │      5 │
│ vlan_properties       │     14 │
│ hsrp_properties       │      0 │
│ mlag_properties       │      0 │
│ ip_owners             │     75 │
│ undefined_references  │      0 │
│ vrrp_properties       │      8 │
╰───────────────────────┴────────╯

╭───────────────┬────────╮
│ Topology      │   Rows │
├───────────────┼────────┤
│ edges         │    120 │
│ layer_1_edges │      0 │
│ layer_3_edges │    120 │
│ network_map   │      1 │
╰───────────────┴────────╯

╭────────────────────────────┬────────╮
│ Routing                    │   Rows │
├────────────────────────────┼────────┤
│ routes                     │   8994 │
│ bgp_process_config         │     12 │
│ bgp_peer_config            │     24 │
│ bgp_session_compatibility  │     24 │
│ bgp_session_status         │     24 │
│ bgp_edges                  │     20 │
│ bgp_ribs                   │   4320 │
│ ospf_process_config        │      6 │
│ ospf_interface_config      │     36 │
│ ospf_area_config           │      6 │
│ ospf_session_compatibility │     20 │
╰────────────────────────────┴────────╯

╭───────────────────┬────────╮
│ Setup             │   Rows │
├───────────────────┼────────┤
│ unconnected_nodes │      3 │
│ ignored_lines     │     49 │
│ file_parse_status │     16 │
│ parse_warnings    │     92 │
│ errors            │      0 │
╰───────────────────┴────────╯

╭────────────────────────┬────────╮
│ Inconsistent Traffic   │   Rows │
├────────────────────────┼────────┤
│ subnet_multipath       │      0 │
│ loopback_multipath     │      0 │
╰────────────────────────┴────────╯

╭──────────┬────────╮
│ Probes   │   Rows │
├──────────┼────────┤
│ probes   │      4 │
╰──────────┴────────╯

$ invariant show probes --json
[
  {
    "target": "8.8.8.8/32",
    "type": "ICMP_ECHO",
    "comment": "Custom 8.8.8.8 ECHO No-Ignore Filters",
    "ignore_filters": false,
    "node_outcomes": {
      "asa": "always",
      "border-1": "always",
      "core-1": "always",
      "core-2": "always",
      "dc-1": "always",
      "dist-1": "always",
      "dist-2": "always",
      "dmzfw-1": "always",
      "dmzsw-1": "always",
      "host-srv-dmz": "always",
      "i-01602d9efaed4409a": "always",
      "i-02cae6eaa9edeed70": "always",
      "i-04cd3db5124a05ee6": "never",
      "i-0a5d64b8b58c6dd09": "never",
      "internet": "always",
      "isp_64501": "always",
      "isp_64502": "always",
      "subnet-009d57c7f13813630": "never",
      "subnet-0333a0749ea4ce3df": "never",
      "subnet-03acae3b9a534fff9": "never",
      "subnet-06005943afe32f714": "never",
      "subnet-06a692ed4ef84368d": "never",
      "subnet-09b389def558a9c7d": "never",
      "subnet-0cb5f4c094bee5214": "never",
      "subnet-0f84a4be105f7aaef": "never",
      "tgw-06b348adabd13452d": "partial",
      "tgw-0888a76c8a371246d": "partial"
    }
  }
]
```

