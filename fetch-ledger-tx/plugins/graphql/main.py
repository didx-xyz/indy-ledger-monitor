from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from schema import Query
import graphene

app = FastAPI()

app.add_route('/graphql', GraphQLApp(schema=graphene.Schema(query=Query)))

@app.get('/')
def ping():
    return {'ping': 'pong'}
