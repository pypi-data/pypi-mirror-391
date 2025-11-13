# klusterinfo

A tool to list k8s nodes from the current context and their resource allocation state.


## Example

```
$ klusterinfo
ip-172-16-46-23.eu-west-2.compute.internal (23/58) pods
	<CPU 8.0 cores [37.62% / 65.00%]>
	<Memory 31267MB [1.27% / 1.91%]>
ip-172-16-47-22.eu-west-2.compute.internal (12/58) pods
	<CPU 8.0 cores [35.12% / 65.00%]>
	<Memory 31267MB [0.82% / 0.82%]>
ip-172-16-79-34.eu-west-2.compute.internal (21/58) pods
	<CPU 8.0 cores [35.12% / 65.00%]>
	<Memory 31267MB [0.82% / 0.82%]>
```

## Output format

The tool lists nodes and displays the allocatable resources on each node below:
```
[nodename] ([running-pods]/[max-pods]) pods
  <CPU [number-of-cpus] cores [[requested cpu %] / [limited cpu %]]>
  <Memory [memory-size] [[requested memory %] / [limited memory %]]>
```

## Status

This tool is not very sophisticated, but since kubectl can not easily display
the aggregated resource requests and limits per node, I needed it.

If this continues to be useful, possible feature improvements might be:

- JSON output
- Group by deployment
  - Within nodes
  - Cluster-wide
