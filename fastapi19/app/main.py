from fastapi import FastAPI , Response , status ,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

while True:
    try:
       conn = psycopg2.connect(host = 'localhost' , database = 'fastapipost' , user = 'postgres' , password = 'Qrzpl1999$', cursor_factory=RealDictCursor)
       cursor = conn.cursor()
       print("connection to db success")
       break
    except Exception as error:
       print("connecting to db failed")
       print("Error", error)
       time.sleep(2)
 

class Post(BaseModel):
    title : str
    content : str
    published : bool = True
    # rating : Optional[int] = None

my_posts = [{'title': 'this is some title' , 'content': 'this is some content' , 'id' : 3}, {'title': 'this is some title2' , 'content': 'this is some content2', 'id' : 2}]

def find_posts(id):
    for p in my_posts:
        if p['id'] == id:
            return p

        
def find_index_to_delete(id):
    for i , p in enumerate(my_posts):
        if p['id'] == id :
            return i

@app.get('/')
def root():
    return {'message' : 'Hello world'}

@app.post('/posts')
def get_posts():
    return {'message' : 'This is your posts'}

@app.get('/posts')
def get_posts():
    return {'message' : my_posts }

@app.post('/createposts')
def create_posts(payload : dict = Body(...)):
    print(payload)
    return {'new post' : f'title is {payload['title']} with content being {payload['content']}'}

@app.post('/createpostsPydantic',status_code=status.HTTP_201_CREATED)
def create_posts(new_post : Post):
    print(new_post.published)
    print(new_post.rating)
    print(new_post.model_dump())
    return {'data' : new_post}


@app.post('/createpostsAppendToMyposts')
def create_posts(new_post : Post):
    posts_dict = new_post.model_dump()
    posts_dict['id'] = randrange(0, 10000)
    my_posts.append(posts_dict)
    return {'data' : posts_dict}

@app.get('/posts/latest')
def latest_posts():
    post = my_posts[len(my_posts)-1]
    return {'detail': post}


@app.get('/posts/{id}')
def get_posts(id : int ,response : Response):
    posts = find_posts(id)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail={ 'message' : f"post with {id} not found"})
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return { 'message' : f"post with {id} not found"}
    print(id)
    return {'message' : posts }

@app.delete('/posts/{id}' , status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id : int):
    i = find_index_to_delete(id)
    if i == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with {id} not found')
    my_posts.pop(i)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/posts/{id}')
def update_posts(id: int , post : Post):
    index = find_index_to_delete(id)
    if index == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with {id} not found')
    post_dict = post.model_dump()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {'data': post_dict}

