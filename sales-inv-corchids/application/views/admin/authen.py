'''
Created on Dec 13, 2016

@author: jason
'''

import base64

from google.appengine.api import users

from application.standard_models import UserModel
from application.rest import Authenticator,DispatcherException,Authorizer

from flask import make_response

AUTHENTICATE_HEADER = "WWW-Authenticate"
AUTHORIZATION_HEADER = "Authorization"
AUTHENTICATE_TYPE = 'Basic realm="Secure Area"'
CONTENT_TYPE_HEADER = "Content-Type"
HTML_CONTENT_TYPE = "text/html"

from werkzeug.security import check_password_hash

class BasicAuthenticator(Authenticator):
    """Example implementation of HTTP Basic Auth."""

    def __init__(self):
        super(BasicAuthenticator, self).__init__()

    def authenticate(self, dispatcher):

        user_arg = None
        pass_arg = None
        curr_user = users.get_current_user()
        if curr_user:  # means you are logged into website
            return curr_user
        try:
            # Parse the header to extract a user/password combo.
            # We're expecting something like "Basic XZxgZRTpbjpvcGVuIHYlc4FkZQ=="
            auth_header = dispatcher.request.headers[AUTHORIZATION_HEADER]

            # Isolate the encoded user/passwd and decode it
            auth_parts = auth_header.split(' ')
            user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
            user_arg = user_pass_parts[0]
            pass_arg = user_pass_parts[1]
            query = UserModel.query(UserModel.username == user_arg)
            user = query.get()
            if check_password_hash(user.pw_hash, pass_arg):
                return users.User(user.added_by)

        except Exception:
            # set the headers requesting the browser to prompt for a user/password:
            #dispatcher.response.set_status(401, message="Authentication Required")
            dispatcher.response = make_response("", 401)
            dispatcher.response.headers[AUTHENTICATE_HEADER] = AUTHENTICATE_TYPE
            dispatcher.response.headers[CONTENT_TYPE_HEADER] = HTML_CONTENT_TYPE

            dispatcher.response.stream.write("<html><body>401 Authentication Required</body></html>")
            raise DispatcherException(401)

        # FIXME, writeme: if(valid user_arg,pass_arg):
        #     return
        

        dispatcher.forbidden()

class OwnerAuthorizer(Authorizer):

    def can_read(self, dispatcher, model):
        if(model.owner != users.get_current_user()):
            dispatcher.not_found()

    def filter_read(self, dispatcher, models):
        return self.filter_models(models)

    def check_query(self, dispatcher, query_expr, query_params):
        #query_params.append(users.get_current_user())
        #if(not query_expr):
        #    query_expr = 'WHERE owner = :%d' % (len(query_params))
        #else:
        #    query_expr += ' AND owner = :%d' % (len(query_params))
        return query_expr

    def can_write(self, dispatcher, model, is_replace):
        if(not model.is_saved()):
            # creating a new model
            model.owner = users.get_current_user()
        elif(model.owner != users.get_current_user()):
            dispatcher.not_found()

    def filter_write(self, dispatcher, models, is_replace):
        return self.filter_models(models)

    def can_delete(self, dispatcher, model_type, model_key):
        query = model_type.all(True).filter("owner = ", users.get_current_user()).filter("__key__ = ", model_key)
        if(len(query.fetch(1)) == 0):
            dispatcher.not_found()

    def filter_models(self, models):
        #cur_user = users.get_current_user()
        #models[:] = [model for model in models if model.owner == cur_user]
        return models