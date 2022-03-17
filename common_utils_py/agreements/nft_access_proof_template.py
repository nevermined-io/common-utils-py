NFT_ACCESS_PROOF_TEMPLATE = {
  "type": "nft-access-proof",
  "templateId": "",
  "name": "nftAccessProofAgreement",
  "description": "This service agreement defines the flow for accessing an asset holding a NFT",
  "creator": "",
  "serviceAgreementTemplate": {
    "contractName": "NFTAccessProofTemplate",
    "events": [
      {
        "name": "AgreementCreated",
        "actorType": "consumer",
        "handler": {
          "moduleName": "nftAccessProofTemplate",
          "functionName": "fulfillNFTHolderCondition",
          "version": "0.1"
        }
      }
    ],
    "fulfillmentOrder": [
      "nftHolder.fulfill",
      "nftAccess.fulfill"
    ],
    "conditionDependency": {
      "nftHolder": [],
      "access": []
    },
    "conditions": [
      {
        "name": "nftHolder",
        "timelock": 0,
        "timeout": 0,
        "contractName": "NFTHolderCondition",
        "functionName": "fulfill",
        "parameters": [
          {
            "name": "_did",
            "type": "bytes32",
            "value": ""
          },
          {
            "name": "_holderAddress",
            "type": "address",
            "value": ""
          },
          {
            "name": "_numberNfts",
            "type": "uint256",
            "value": ""
          }
        ],
        "events": [
          {
            "name": "Fulfilled",
            "actorType": "publisher",
            "handler": {
              "moduleName": "nftHolderCondition",
              "functionName": "fulfillNFTHolderCondition",
              "version": "0.1"
            }
          }
        ]
      },
      {
        "name": "access",
        "timelock": 0,
        "timeout": 0,
        "contractName": "AccessProofCondition",
        "functionName": "fulfill",
        "events": [],
        "parameters": [
          {
            "name": "_hash",
            "type": "uint",
            "value": ""
          },
          {
            "name": "_grantee",
            "type": "uint[2]",
            "value": ""
          },
          {
            "name": "_provider",
            "type": "uint[2]",
            "value": ""
          },
          {
            "name": "_cipher",
            "type": "uint[2]",
            "value": ""
          },
          {
            "name": "_proof",
            "type": "bytes",
            "value": ""
          }
        ]
      }
    ]
  }
}