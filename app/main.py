from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key
import boto3
import os

# Initialize FastAPI
app = FastAPI()

# Allowed origins
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow credentials (e.g., cookies)
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# AWS CONFIG
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION')

# DynamoDB Configuration
dynamodb = boto3.resource(
    "dynamodb", 
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
TABLE_NAME = "group-two-dev-poll"
table = dynamodb.Table(TABLE_NAME)

# Models
class CreatePoll(BaseModel):
    id: str
    title: str
    options: list

class VotePoll(BaseModel):
    options: list

class VoteUserPoll(BaseModel):
    id: str
    channel_id: str
    poll_id: int

class CreateUser(BaseModel):
    id: str
    channel_id: str
    name: str

@app.post("/poll")
async def create_poll(body: CreatePoll):

    pk = f"poll"
    sk = f"channel-{body.id}"
    
    try:
        table.put_item(
            Item={
                "PK": pk,
                "SK": sk,
                "ID": body.id,
                "Title": body.title,
                "Options": body.options
            }
        )
        return {"message": "Successfully Created!."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/poll/{id}")
async def get_poll(id: str):
    pk = f"poll"
    sk = f"channel-{id}"
    
    try:
        response = table.get_item(Key={"PK": pk, "SK": sk})
        item = response.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/poll/vote/{id}")
async def vote_poll(body: VotePoll, id: str):
    pk = f"poll"
    sk = f"channel-{id}"
    
    try:
        response = table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET #options = :options",
            ExpressionAttributeNames={"#options": "Options"},
            ExpressionAttributeValues={":options": body.options},
            ReturnValues="UPDATED_NEW"
        )
        return {"message": "Successfully Updated!", "data": response["Attributes"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/user")
async def create_user(body: CreateUser):
    pk = f"channel-{body.channel_id}"
    sk = f"user-{body.id}"
    
    try:
        table.put_item(
            Item={
                "PK": pk,
                "SK": sk,
                "ID": body.id,
                "Name": body.name
            }
        )
        return {"message": "Successfully Created!."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/user/list/{channel_id}")
async def user_lists(channel_id: str):
    pk = f"channel-{channel_id}"
    sk = f"user-"
    
    try:
        response = table.query(
            KeyConditionExpression=Key('PK').eq(pk) & Key('SK').begins_with(sk)
        )
        return response['Items']
    except Exception as e:
        print(f"Error querying items: {e}")
        return []


@app.put("/user/vote")
async def vote_user_poll(body: VoteUserPoll):
    pk = f"channel-{body.channel_id}"
    sk = f"user-{body.id}"
    
    try:
        vote_details = await get_user_vote(body.channel_id, body.id)

        if vote_details:
            poll_id = vote_details.get("PollID", None)
            is_voted = vote_details.get("Voted", True)

            if poll_id:
                # Check if same poll id meaning removed vote and set to false
                is_voted = not is_voted if poll_id == body.poll_id else True

            response = table.update_item(
                Key={"PK": pk, "SK": sk},
                UpdateExpression="SET #poll_id = :poll_id, #voted = :voted",
                ExpressionAttributeNames={
                    "#poll_id": "PollID",
                    "#voted": "Voted"
                },
                ExpressionAttributeValues={
                    ":poll_id": body.poll_id,
                    ":voted": is_voted
                },
                ReturnValues="UPDATED_NEW"
            )
            return {"message": "Successfully Updated!", "data": response["Attributes"]}
        else:
            return {"message": "No User Found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_user_vote(channel_id: str, user_id: str):
    pk = f"channel-{channel_id}"
    sk = f"user-{user_id}"
    
    try:
        response = table.get_item(Key={"PK": pk, "SK": sk})
        item = response.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
