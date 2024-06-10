from pydantic import BaseModel

from event_listener import EventListener


app = EventListener(
    'localhost:9092',
    group_id='event-listeer-test-group'
)


class User(BaseModel):
    name: str
    email: str


class Address(BaseModel):
    city: str
    street: str
    location_code: str


@app.topic('User')
async def log_user_details(user: User, user_address: Address):
    print(f'{user!r}, {user_address!r}')

if __name__ == '__main__':
    app.run()
