
import asyncio
import socketio

import collections import defaultdict,namedtuple

from sanic import Sanic
from sanic.response import json

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)


User = namedtuple('User', 'sid username avatar status')

users = defaultdict(User)


class HongpaNamespace(socketio.AsyncNamespace):

    def on_connect(self,sid,environ):
        print('connect ' + sid)
        print(environ)

    def on_disconnect(self,sid):
        print('disconnect ' + sid)
        users.pop(sid,None)

    async def on_login(self,sid,data):

        username = data['username']

        user = User()
        user.username = username
        user.avatar = 'https://api.adorable.io/avatars/200/' + username
        user.sid = sid

        users[sid] = user

        await self.emit('logined', {'user':user._asdict(),'code':0}, room=sid)

        for ssid in self.manager.get_participants(self, sid)
            print(ssid)


    async def on_create(self,sid,data):
        rooms = self.manager.rooms[None].keys()

        print('rooms ', rooms)
        rooms_data = []
        """
        {
        sid:str,
        user:user,
        users:users
        }
        """
        for room in rooms:
            sids = self.manager.rooms[None][room].keys()
            print('sids ', sids)
            users = [users[s]._asdict() for s in sids]
            _room = {'sid':room}
            _room['user'] = users[room]._asdict()
            _room['users'] = users
            rooms_data.append(_room)

        await self.emit('rooms',{'rooms':rooms,'code':0},room=sid)


    async def on_join(self,sid,data):

        room_sid = data['sid']
        self.enter_room(sid,room_sid)

        # need to do  add room is full

        user = users.get(sid)

        await self.emit('user_joined',{'user':user._asdict(),'code':0},room=room_sid,skip_sid=sid)


    async def on_leave(self,sid,data):

        room_sid = data['sid']
        if sid == room_sid:
            return

        self.leave_room(sid,room_sid)

        user = users.get(sid)

        await self.emit('user_leaved',{'user':user._asdict(),'code':0},room=room_sid,skip_sid=sid)



@app.listener('before_server_start')
def before_server_start(app, loop):
    print('before server start')


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    print('after server stop')

@app.middleware('response')
async def auth(request, response):
    print(request.json)
    print('middleware')



@sio.on('connect')
async def on_connect(sid, environ):
    print('on_connect')
    print(environ)



@sio.on('disconnect')
async def on_disconnect(sid):
    print('on_disconnect')


@sio.on('login')
async def on_login(sid,message):

    username = message['username']
    user = User()
    user.username = username
    user.avatar = 'https://api.adorable.io/avatars/200/' + username
    user.sid = sid

    users[sid] = user

    await sio.emit('joined', {'data':user._asdict()}, room=sid)




@sio.on('create')
async def on_create(sid, message):
    print('join ' + sid)
    print('message ' + str(message))


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6001)
