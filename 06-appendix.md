1. 2 API endpoints
    1. **POST** */secrets*
        1. Vars
            1. message - required - The message to encrypt
            1. passphrase - required - The passphrase for the message
            1. expiration_time - optional - How long for the message to persist in seconds. Default is 604800
        1. Returns JSON
            1. Vars
                1. id - unique ID of the secret for retrieval
                1. success - Boolean
        1. **POST** */secrets/<id>*
            1. Vars
                1. passphrase - required - The passphrase to unlock the secret
            1. Returns JSON
                1. Vars
                    1. message - The decrypted message
                    1. success - Boolean
    1. If the message doesn't exist, has already been read, or has expired
        ```json
        {
            "message": "This secret either never existed or it was already read",
            "success": "False"
        }
        ```