# apieasy

A tiny, simple REST API framework for Python using decorators.  
No Flask. No FastAPI.  
Define endpoints using clean, minimal code.

## Example

from apieasy import get, post, run

@get("/hello")
def hello():
    return {"message": "Hello World"}

run()

## Installation

pip install apieasy

## Usage

apieasy run

## Features
- Define routes with decorators
- Auto JSON response
- Minimal routing engine
