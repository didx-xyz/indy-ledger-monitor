from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from .schema import schema
import graphene

app = FastAPI()

app.add_route('/graphql', GraphQLApp(schema=schema))

@app.get('/')
def ping():
    return {'API': '/graphql'}
