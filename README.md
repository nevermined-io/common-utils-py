[![banner](https://raw.githubusercontent.com/nevermined-io/assets/main/images/logo/banner_logo.png)](https://nevermined.io)

# Nevermined Python common utils 
Provides common functions to interact with Nevermined ecosystem

[![PyPI](https://img.shields.io/pypi/v/common-utils-py.svg)](https://pypi.org/project/common-utils-py/)

## Main components
* DID and DDO
  * DID format: 'did:nv:<32bytes-hex-representation>
  * DID is the universal identifier for assets in the Nevermined network
  * DDO is the json document that 
* DID resolver
  * Given a valid did, returns the associated DDO document which define 
    the asset metadata and other services offered for the asset
* Metadata
* Service Agreements

## Attribution
This project is based in the [Ocean Protocol Common-utils-py](https://github.com/oceanprotocol/common-utils-py). It keeps the same Apache v2 License and adds some improvements.


## License

```text
Copyright 2020 Keyko GmbH.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
