ACCESS_PROOF_SLA_TEMPLATE = {
  "type": "access-proof",
  "templateId": "",
  "name": "dataAssetAccessServiceAgreement",
  "description": "This service agreement defines the flow for accessing a data asset on the network. Any file or bundle of files can be access using this service agreement",
  "creator": "",
  "serviceAgreementTemplate": {
    "contractName": "AccessProofTemplate",
    "events": [
      {
        "name": "AgreementCreated",
        "actorType": "consumer",
        "handler": {
          "moduleName": "escrowAccessTemplate",
          "functionName": "fulfillLockPaymentCondition",
          "version": "0.1"
        }
      }
    ],
    "fulfillmentOrder": [
      "lockPayment.fulfill",
      "access.fulfill",
      "escrowPayment.fulfill"
    ],
    "conditionDependency": {
      "lockPayment": [],
      "access": [],
      "escrowPayment": [
        "lockPayment",
        "access"
      ]
    },
    "conditions": [
      {
        "name": "lockPayment",
        "timelock": 0,
        "timeout": 0,
        "contractName": "LockPaymentCondition",
        "functionName": "fulfill",
        "parameters": [
          {
            "name": "_did",
            "type": "bytes32",
            "value": ""
          },
          {
            "name": "_rewardAddress",
            "type": "address",
            "value": ""
          },
          {
            "name": "_tokenAddress",
            "type": "address",
            "value": ""
          },
          {
            "name": "_amounts",
            "type": "uint256[]",
            "value": []
          },
          {
            "name": "_receivers",
            "type": "address[]",
            "value": []
          }
        ],
        "events": [
          {
            "name": "Fulfilled",
            "actorType": "publisher",
            "handler": {
              "moduleName": "lockPaymentCondition",
              "functionName": "fulfillAccessCondition",
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
        ],
        "events": [
          {
            "name": "Fulfilled",
            "actorType": "publisher",
            "handler": {
              "moduleName": "access",
              "functionName": "fulfillEscrowPaymentCondition",
              "version": "0.1"
            }
          },
          {
            "name": "TimedOut",
            "actorType": "consumer",
            "handler": {
              "moduleName": "access",
              "functionName": "fulfillEscrowPaymentCondition",
              "version": "0.1"
            }
          }
        ]
      },
      {
        "name": "escrowPayment",
        "timelock": 0,
        "timeout": 0,
        "contractName": "EscrowPayment",
        "functionName": "fulfill",
        "parameters": [
          {
            "name": "_did",
            "type": "bytes32",
            "value": ""
          },
          {
            "name": "_amounts",
            "type": "uint256[]",
            "value": []
          },
          {
            "name": "_receivers",
            "type": "address[]",
            "value": []
          },
          {
            "name": "_sender",
            "type": "address",
            "value": ""
          },
          {
            "name": "_tokenAddress",
            "type": "address",
            "value": ""
          },
          {
            "name": "_lockCondition",
            "type": "bytes32",
            "value": ""
          },
          {
            "name": "_releaseCondition",
            "type": "bytes32",
            "value": ""
          }
        ],
        "events": [
          {
            "name": "Fulfilled",
            "actorType": "publisher",
            "handler": {
              "moduleName": "escrowPaymentCondition",
              "functionName": "verifyRewardTokens",
              "version": "0.1"
            }
          }
        ]
      }
    ]
  }
}