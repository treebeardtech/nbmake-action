# Using output data

Files saved to any configured output directories can be accessed through the web UI and via an API endpoint.

A `GET` request to an output endpoint will download the output file.

```bash
curl -o output_2.txt \
https://api.treebeard.io/63db2b28e1/example/6ef52a33-ff79-431c-8d9b-50d66902eaad/another_output/output_2.txt\?api_key\=xxxxxxxxxx
```

NOTE: The API links generated in the web page are not shareable, they contain your API Key. Whilst this is only one part of your authentication key, please do not share it.
