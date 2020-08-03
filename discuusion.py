# -*-coding:utf-8-*-
import mimetypes
import os
import re

import requests

from rocketchat_API.APIExceptions.RocketExceptions import RocketConnectionException, RocketAuthenticationException, \
    RocketMissingParamException


class RocketChat:
    API_path = '/api/v1/'

    def __init__(self, user=None, password=None, auth_token=None, user_id=None,
                 server_url='http://18.222.56.119', ssl_verify=True, proxies=None,
                 timeout=30, session=None):
        """Creates a RocketChat object and does login on the specified server"""
        self.headers = {}
        self.server_url = server_url
        self.proxies = proxies
        self.ssl_verify = ssl_verify
        self.timeout = timeout
        self.req = session or requests
        if user and password:
            self.login(user, password)  # skipcq: PTC-W1006
        if auth_token and user_id:
            self.headers['X-Auth-Token'] = auth_token
            self.headers['X-User-Id'] = user_id

    @staticmethod
    def __reduce_kwargs(kwargs):
        if 'kwargs' in kwargs:
            for arg in kwargs['kwargs'].keys():
                kwargs[arg] = kwargs['kwargs'][arg]

            del kwargs['kwargs']
        return kwargs

    def __call_api_get(self, method, **kwargs):
        args = self.__reduce_kwargs(kwargs)
        url = self.server_url + self.API_path + method
        # convert to key[]=val1&key[]=val2 for args like key=[val1, val2], else key=val
        params = '&'.join(
            '&'.join(i + '[]=' + j for j in args[i])
            if isinstance(args[i], list)
            else i + '=' + str(args[i])
            for i in args
        )
        return self.req.get(
            '%s?%s' % (url, params),
            headers=self.headers,
            verify=self.ssl_verify,
            proxies=self.proxies,
            timeout=self.timeout
        )

    def __call_api_post(self, method, files=None, use_json=True, **kwargs):
        reduced_args = self.__reduce_kwargs(kwargs)
        # Since pass is a reserved word in Python it has to be injected on the request dict
        # Some methods use pass (users.register) and others password (users.create)
        if 'password' in reduced_args and method != 'users.create':
            reduced_args['pass'] = reduced_args['password']
        if use_json:
            return self.req.post(self.server_url + self.API_path + method,
                                 json=reduced_args,
                                 files=files,
                                 headers=self.headers,
                                 verify=self.ssl_verify,
                                 proxies=self.proxies,
                                 timeout=self.timeout
                                 )
        else:
            return self.req.post(self.server_url + self.API_path + method,
                                 data=reduced_args,
                                 files=files,
                                 headers=self.headers,
                                 verify=self.ssl_verify,
                                 proxies=self.proxies,
                                 timeout=self.timeout
                                 )

    # Authentication

    def login(self, user, password):
        request_data = {
            'password': password
        }
        if re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', user):
            request_data['user'] = user
        else:
            request_data['username'] = user
        login_request = requests.post(self.server_url + self.API_path + 'login',
                                      data=request_data,
                                      verify=self.ssl_verify,
                                      proxies=self.proxies)
        if login_request.status_code == 401:
            raise RocketAuthenticationException()

        if login_request.status_code == 200:
            if login_request.json().get('status') == "success":
                self.headers['X-Auth-Token'] = login_request.json().get('data').get('authToken')
                self.headers['X-User-Id'] = login_request.json().get('data').get('userId')
                return login_request
            else:
                raise RocketAuthenticationException()
        else:
            raise RocketConnectionException()

    def me(self, **kwargs):
        """	Displays information about the authenticated user."""
        return self.__call_api_get('me', kwargs=kwargs)

    def logout(self, **kwargs):
        """Invalidate your REST rocketchat_API authentication token."""
        return self.__call_api_post('logout', kwargs=kwargs)

    # Miscellaneous information

    def info(self, **kwargs):
        """Information about the Rocket.Chat server."""
        return self.__call_api_get('info', kwargs=kwargs)

    # Users

    def users_info(self, user_id=None, username=None, **kwargs):
        """Gets a user’s information, limited to the caller’s permissions."""
        if user_id:
            return self.__call_api_get('users.info', userId=user_id, kwargs=kwargs)
        elif username:
            return self.__call_api_get('users.info', username=username, kwargs=kwargs)
        else:
            raise RocketMissingParamException('userID or username required')

    def users_list(self, **kwargs):
        """All of the users and their information, limited to permissions."""
        return self.__call_api_get('users.list', kwargs=kwargs)


    def users_create(self, email, name, password, username, **kwargs):
        """Creates a user"""
        return self.__call_api_post('users.create', email=email, name=name, password=password, username=username,
                                    kwargs=kwargs)

    def users_delete(self, user_id, **kwargs):
        """Deletes a user"""
        return self.__call_api_post('users.delete', userId=user_id, **kwargs)

    def users_register(self, email, name, password, username, **kwargs):
        """Register a new user."""
        return self.__call_api_post('users.register', email=email, name=name, password=password, username=username,
                                    kwargs=kwargs)

    def users_forgot_password(self, email, **kwargs):
        """Send email to reset your password."""
        return self.__call_api_post('users.forgotPassword', email=email, data=kwargs)

    # Chat

    def chat_post_message(self, text, room_id=None, channel=None, **kwargs):
        """Posts a new chat message."""
        if room_id:
            if text:
                return self.__call_api_post('chat.postMessage', roomId=room_id,
                                            text=text, kwargs=kwargs)
            return self.__call_api_post('chat.postMessage', roomId=room_id,
                                        kwargs=kwargs)
        elif channel:
            if text:
                return self.__call_api_post('chat.postMessage',
                                            channel=channel, text=text,
                                            kwargs=kwargs)
            return self.__call_api_post('chat.postMessage',
                                        channel=channel, kwargs=kwargs)
        else:
            raise RocketMissingParamException('roomId or channel required')

    def chat_get_message(self, msg_id, **kwargs):
        return self.__call_api_get('chat.getMessage', msgId=msg_id, kwargs=kwargs)
    
    def chat_send_msg(self,room_id,msg,**kwargs):
        return self.__call_api_post('chat.sendMessage', message={'rid':room_id, 'msg':msg}, kwargs=kwargs)


    def chat_react(self, msg_id, emoji='smile', **kwargs):
        """Updates the text of the chat message."""
        return self.__call_api_post('chat.react', messageId=msg_id, emoji=emoji, kwargs=kwargs)


    def chat_get_message_read_receipts(self, message_id, **kwargs):
        """Get Message Read Receipts"""
        return self.__call_api_get('chat.getMessageReadReceipts', messageId=message_id, kwargs=kwargs)

    # Channels

    def channels_list(self, **kwargs):
        """Retrieves all of the channels from the server."""
        return self.__call_api_get('channels.list', kwargs=kwargs)

    def channels_info(self, room_id=None, channel=None, **kwargs):
        """Gets a channel’s information."""
        if room_id:
            return self.__call_api_get('channels.info', roomId=room_id, kwargs=kwargs)
        elif channel:
            return self.__call_api_get('channels.info', roomName=channel, kwargs=kwargs)
        else:
            raise RocketMissingParamException('roomId or channel required')

    def channels_history(self, room_id, **kwargs):
        """Retrieves the messages from a channel."""
        return self.__call_api_get('channels.history', roomId=room_id, kwargs=kwargs)

    def channels_open(self, room_id, **kwargs):
        """Adds the channel back to the user’s list of channels."""
        return self.__call_api_post('channels.open', roomId=room_id, kwargs=kwargs)

    def channels_create(self, name, **kwargs):
        """Creates a new public channel, optionally including users."""
        return self.__call_api_post('channels.create', name=name, kwargs=kwargs)

    def channels_invite(self, room_id, user_id, **kwargs):
        """Adds a user to the channel."""
        return self.__call_api_post('channels.invite', roomId=room_id, userId=user_id, kwargs=kwargs)

    def channels_join(self, room_id, join_code, **kwargs):
        """Joins yourself to the channel."""
        return self.__call_api_post('channels.join', roomId=room_id, joinCode=join_code, kwargs=kwargs)

    def channels_kick(self, room_id, user_id, **kwargs):
        """Removes a user from the channel."""
        return self.__call_api_post('channels.kick', roomId=room_id, userId=user_id, kwargs=kwargs)

    def channels_leave(self, room_id, **kwargs):
        """Causes the callee to be removed from the channel."""
        return self.__call_api_post('channels.leave', roomId=room_id, kwargs=kwargs)

    def channels_rename(self, room_id, name, **kwargs):
        """Changes the name of the channel."""
        return self.__call_api_post('channels.rename', roomId=room_id, name=name, kwargs=kwargs)

    def channels_set_join_code(self, room_id, join_code, **kwargs):
        """Sets the code required to join the channel."""
        return self.__call_api_post('channels.setJoinCode', roomId=room_id, joinCode=join_code, kwargs=kwargs)

    def channels_members(self, room_id=None, channel=None, **kwargs):
        """Lists all channel users."""
        if room_id:
            return self.__call_api_get('channels.members', roomId=room_id, kwargs=kwargs)
        elif channel:
            return self.__call_api_get('channels.members', roomName=channel, kwargs=kwargs)
        else:
            raise RocketMissingParamException('roomId or channel required')

    def channels_roles(self, room_id=None, room_name=None, **kwargs):
        """Lists all user’s roles in the channel."""
        if room_id:
            return self.__call_api_get('channels.roles', roomId=room_id, kwargs=kwargs)
        elif room_name:
            return self.__call_api_get('channels.roles', roomName=room_name, kwargs=kwargs)
        else:
            raise RocketMissingParamException('roomId or room_name required')

    # Groups

    def groups_list_all(self, **kwargs):
        """
        List all the private groups on the server.
        The calling user must have the 'view-room-administration' right
        """
        return self.__call_api_get('groups.listAll', kwargs=kwargs)

    def groups_list(self, **kwargs):
        """List the private groups the caller is part of."""
        return self.__call_api_get('groups.list', kwargs=kwargs)

    def groups_create(self, name, **kwargs):
        """Creates a new private group, optionally including users, only if you’re part of the group."""
        return self.__call_api_post('groups.create', name=name, kwargs=kwargs)

    def groups_info(self, room_id=None, room_name=None, **kwargs):
        """GRetrieves the information about the private group, only if you’re part of the group."""
        if room_id:
            return self.__call_api_get('groups.info', roomId=room_id, kwargs=kwargs)
        elif room_name:
            return self.__call_api_get('groups.info', roomName=room_name, kwargs=kwargs)
        else:
            raise RocketMissingParamException('roomId or roomName required')

    def groups_invite(self, room_id, user_id, **kwargs):
        """Adds a user to the private group."""
        return self.__call_api_post('groups.invite', roomId=room_id, userId=user_id, kwargs=kwargs)

    def groups_kick(self, room_id, user_id, **kwargs):
        """Removes a user from the private group."""
        return self.__call_api_post('groups.kick', roomId=room_id, userId=user_id, kwargs=kwargs)

    def groups_leave(self, room_id, **kwargs):
        """Causes the callee to be removed from the private group, if they’re part of it and are not the last owner."""
        return self.__call_api_post('groups.leave', roomId=room_id, kwargs=kwargs)

    def groups_open(self, room_id, **kwargs):
        """Adds the private group back to the user’s list of private groups."""
        return self.__call_api_post('groups.open', roomId=room_id, kwargs=kwargs)

    def groups_members(self, room_id=None, group=None, **kwargs):
        """Lists all group users."""
        if room_id:
            return self.__call_api_get('groups.members', roomId=room_id, kwargs=kwargs)
        elif group:
            return self.__call_api_get('groups.members', roomName=group, kwargs=kwargs)
        else:
            raise RocketMissingParamException('roomId or group required')

    # Rooms

    def rooms_upload(self, rid, file, **kwargs):
        """Post a message with attached file to a dedicated room."""
        files = {
            'file': (os.path.basename(file), open(file, 'rb'), mimetypes.guess_type(file)[0]),
        }
        return self.__call_api_post('rooms.upload/' + rid, kwargs=kwargs, use_json=False, files=files)

    def rooms_get(self, **kwargs):
        """Get all opened rooms for this user."""
        return self.__call_api_get('rooms.get', kwargs=kwargs)
    
    def rooms_create_Discussion(self, room_id, name, reply=None, **kwargs):
        return self.__call_api_post('rooms.createDiscussion', prid=room_id, t_name=name, reply=reply, kwargs=kwargs)
    
    def rooms_get_Discussion(self, room_id, **kwargs):
        return self.__call_api_get('rooms.getDiscussions', roomId=room_id, kwargs=kwargs)

    def rooms_info(self, room_id=None, room_name=None):
        """Retrieves the information about the room."""
        if room_id is not None:
            return self.__call_api_get('rooms.info', roomId=room_id)
        elif room_name is not None:
            return self.__call_api_get('rooms.info', roomName=room_name)
        else:
            raise RocketMissingParamException('roomId or roomName required')

    def rooms_admin_rooms(self, **kwargs):
        """ Retrieves all rooms (requires the view-room-administration permission)."""
        return self.__call_api_get('rooms.adminRooms', kwargs=kwargs)
