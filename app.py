
import socketio
from pprint import pprint
from socketio import asyncio_manager

from aiohttp import web

from collections import defaultdict,namedtuple


manager = asyncio_manager.AsyncManager()

sio = socketio.AsyncServer(client_manager=manager,
        logger=False,
        async_mode='aiohttp')

app = web.Application()
sio.attach(app)


User = namedtuple('User', 'sid username avatar')

users = {}


class HongpaNamespace(socketio.AsyncNamespace):

    def on_connect(self,sid,environ):
        print('connect ' + sid)

    def on_disconnect(self,sid):
        print('disconnect ' + sid)
        users.pop(sid,None)
        manager.leave_room(sid,'/',sid)

    async def on_login(self,sid,data):

        print(type(data),data)
        username = data['username']
        avatar = 'https://api.adorable.io/avatars/200/' + username

        user = User(sid=sid,username=username,avatar=avatar)

        users[sid] = user

        send_message = {'user':user._asdict(),'code':0}

        print(send_message)

        await self.emit('logined', send_message, room=sid)



    async def on_create(self,sid,data):

        print('create ', sid, data)
        print(manager.rooms)

        rooms = manager.rooms['/'].keys()

        print('create ', data, rooms)

        rooms_data = []
        for room in rooms:
            sids = manager.rooms['/'][room].keys()
            if users.get(room) == None:
                continue
            print('sids ', sids)
            us = [users[s]._asdict() for s in sids]
            _room = {'sid':room}
            _room['user'] = users[room]._asdict()
            _room['users'] = us
            rooms_data.append(_room)

        print(rooms_data)

        await self.emit('rooms',{'rooms':rooms_data,'code':0},room=sid)


    async def on_join(self,sid,data):

        print('join ', data)

        room_sid = data['sid']
        self.enter_room(sid,room_sid)

        # need to do  add room is full

        user = users.get(sid)

        await self.emit('user_joined',{'user':user._asdict(),'code':0},room=room_sid,skip_sid=sid)


    async def on_leave(self,sid,data):

        print('leave ', data)

        room_sid = data['sid']
        if sid == room_sid:
            return

        self.leave_room(sid,room_sid)
        user = users.get(sid)

        await self.emit('user_leaved',{'user':user._asdict(),'code':0},room=room_sid,skip_sid=sid)


    async def on_message(self,sid,data):

        print('on_message ', sid, data)


#@app.listener('before_server_start')
def before_server_start(app, loop):
    print('before server start')


#@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    print('after server stop')

#@app.middleware('response')
async def auth(request, response):
    print('middleware')


sio.register_namespace(HongpaNamespace())


if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=6001)
    web.run_app(app,host='0.0.0.0',port=6001)
