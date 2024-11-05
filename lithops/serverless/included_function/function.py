def default_function(id, payload, storage):
    print(payload)
    return {
        'statusCode': 200,
        'body': "Function just returns after loading dependencies"
    }
