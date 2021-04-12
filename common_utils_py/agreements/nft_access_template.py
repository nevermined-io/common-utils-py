NFT_ACCESS_TEMPLATE = {
  "type": "nft-access",
  "templateId": "",
  "name": "nftAccessAgreement",
  "description": "This service agreement defines the flow for accessing an access holding a NFT",
  "creator": "",
  "serviceAgreementTemplate": {
    "contractName": "NFTAccessTemplate",
    "events": [
      {
        "name": "AgreementCreated",
        "actorType": "consumer",
        "handler": {
          "moduleName": "nftAccessTemplate",
          "functionName": "fulfillNFTHolderCondition",
          "version": "0.1"
        }
      }
    ],
    "fulfillmentOrder": [
      "nftHolder.fulfill",
      "access.fulfill"
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
        "contractName": "AccessCondition",
        "functionName": "fulfill",
        "parameters": [
          {
            "name": "_documentId",
            "type": "bytes32",
            "value": ""
          },
          {
            "name": "_grantee",
            "type": "address",
            "value": ""
          }
        ],
        "events": [
          {
            "name": "Fulfilled",
            "actorType": "publisher",
            "handler": {
              "moduleName": "access",
              "functionName": "fulfillAccessCondition",
              "version": "0.1"
            }
          },
          {
            "name": "TimedOut",
            "actorType": "consumer",
            "handler": {
              "moduleName": "access",
              "functionName": "fulfillAccessCondition",
              "version": "0.1"
            }
          }
        ]
      }
    ]
  }
}