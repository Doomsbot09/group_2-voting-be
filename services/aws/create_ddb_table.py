import boto3

def create_table():
    dynamodb = boto3.resource('dynamodb', region_name='ap-east-1')

    table_name = 'group-two-dev-poll'

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},  # Partition Key
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}  # Sort Key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},  # String
                {'AttributeName': 'SK', 'AttributeType': 'S'}  # String
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating table {table_name}...")
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table()
