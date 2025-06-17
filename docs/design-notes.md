# Design Notes

The first version intentionally uses simple percentile calculation over retained samples. This is easier to audit in tests. A future high-volume mode can add streaming histograms without changing the public report schema.

The HTTP adapter is template based instead of provider specific because speech gateways vary widely in request format.
