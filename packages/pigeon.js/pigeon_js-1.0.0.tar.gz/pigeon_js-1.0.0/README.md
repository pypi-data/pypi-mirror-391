# pigeon.js

`pigeon.js` is a JavaScript [Pigeon](https://github.com/AllenInstitute/pigeon) client. Also included is a Python script for converting the Python Pigeon message definitions to JSON.

### Message Converter

The message converter can be installed using `pip install .`, then run using `pigeon.js <entrypoint>` or `python -m pigeon_js <entrypoint>`, where `<entrypoint>` is the name of the Python entrypoint containing the message definitions. This produces a JSON file containing the message hashes and schemas in JSON Schema format.

### JavaScript Client

The JavaScript Client uses [`STOMP.js`](https://github.com/stomp-js/stompjs) for STOMP communication and [`ajv`](https://www.npmjs.com/package/ajv) for data validation.

### Example

An example of how this client can be used is available in the `example` directory.
