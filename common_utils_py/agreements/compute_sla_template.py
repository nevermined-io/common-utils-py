COMPUTE_SLA_TEMPLATE = {
  "type": "Compute",
  "templateId": "",
  "name": "dataAssetComputeExecutionAgreement",
  "description": "",
  "creator": "",
  "serviceAgreementTemplate": {
    "contractName": "EscrowComputeExecutionTemplate",
    "events": [
      {
        "name": "AgreementCreated",
        "actorType": "consumer",
        "handler": {
          "moduleName": "EscrowComputeExecutionTemplate",
          "functionName": "fulfillLockPaymentCondition",
          "version": "0.1"
        }
      }
    ],
    "fulfillmentOrder": [
      "lockPayment.fulfill",
      "execCompute.fulfill",
      "escrowPayment.fulfill"
    ],
    "conditionDependency": {
      "lockPayment": [],
      "execCompute": [],
      "escrowPayment": [
        "lockPayment",
        "execCompute"
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
                    "value": "{parameter.assetId}"
                },
                {
                    "name": "_rewardAddress",
                    "type": "address",
                    "value": "{contract.EscrowPayment.address}"
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
                        "functionName": "fulfillExecComputeCondition",
                        "version": "0.1"
                    }
                }
            ]
        },
        {
            "name": "execCompute",
            "timelock": 0,
            "timeout": 0,
            "contractName": "ComputeExecutionCondition",
            "functionName": "fulfill",
            "parameters": [
                {
                    "name": "_documentId",
                    "type": "bytes32",
                    "value": "{parameter.assetId}"
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
                        "functionName": "fulfillEscrowPaymentCondition",
                        "version": "0.1"
                    }
                },
                {
                    "name": "TimedOut",
                    "actorType": "consumer",
                    "handler": {
                        "moduleName": "execCompute",
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
                    "value": "{parameter.assetId}"
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
                    "value": "{contract.LockPaymentCondition.address}"
                },
                {
                    "name": "_releaseCondition",
                    "type": "bytes32",
                    "value": "{contract.ExecComputeCondition.address}"
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