#!/bin/bash 

HOST='10.223.155.43'
TIME=10
USERNAME="test"
PASSWORD="intel123"
PORT="22"
TARGET='10.223.155.69'
RATE='1'
DISPLAY_FREQUENCY='1'
COUNT=0
BATCHES='400'
EXCLUDE='192.168.1.22'

intkey_service="sawtooth-intkey-tp-python.service"
validator_service="sawtooth-validator.service"

`python3 -c 'from sawtooth_rest_api.protobuf import *;'`

python3 -c 'header = TransactionHeader(signer_public_key=signer.get_public_key().as_hex(),
	        family_name='intkey',
	        family_version='1.0',
	        inputs=[addr],
	        outputs=[addr],
	        dependencies=deps,
	        payload_sha512=payload.sha512(),
	        batcher_public_key=signer.get_public_key().as_hex())'

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    transaction = Transaction(
        header=header_bytes,
        payload=payload.to_cbor(),
        header_signature=signature)

