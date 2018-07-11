from websocket_server import WebsocketServer
import MySQLdb as mdb
import re

from config import ws_config

valid_clients = ['205.250.51.208','142.4.208.99','72.213.52.229','71.197.181.249','74.87.206.164','174.66.179.120','67.244.138.127','24.52.46.130','5.196.23.89','174.127.238.136','166.137.98.85']
skip_security = True

def register_client(client, key):
	try:
		con = mdb.connect(ws_config['db']['addr'],ws_config['db']['user'], ws_config['db']['pass'], ws_config['db']['db'])
		with con:
			cur = con.cursor(mdb.cursors.DictCursor)
			cur.execute("SELECT user, secret FROM tokens WHERE token = %s",(key,))
			result = cur.fetchone()
	except mdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		return None
	finally:
		if con:
			con.close()

	if result:
		client['token'] = result['secret']
		return result['user']
	return None

def register_server(client, secret):
	print "Registering Server (" + secret + ")"
        try:
                con = mdb.connect(ws_config['db']['addr'],ws_config['db']['user'], ws_config['db']['pass'], ws_config['db']['db'])
                with con:
                        cur = con.cursor(mdb.cursors.DictCursor)
                        cur.execute("SELECT user, secret FROM tokens WHERE secret = %s",(secret,))
                        result = cur.fetchone()
        except mdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
                return None
        finally:
                if con:
                        con.close()

        if result:
                client['token'] = result['secret']
		client['can_send'] = True
		print "Success!"
                return result['user']
        return None


# Called for every client connecting (after handshake)
def new_client(client, server):
	print("New client connected and was given id %d" % client['id'])
	print client


# Called for every client disconnecting
def client_left(client, server):
	print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
	global valid_clients
	# Check for a REGISTER message
	#TODO: make the match stricter to enforce format
	print("Received: [" + message + "]")
	key = re.search('KEY:[\s]*(.*)', message)
	auth = re.search('AUTH:[\s]*(.*)',message)
	if key:
		print "Matched KEY"
		name = register_client(client, key.group(1))
		if name:
			server.send_message(client, '{"result": "success"}')
			print("Client Registered for: " + name)
		else:
			server.send_message(client, '{"result": "failed"}')
	elif auth:
		print "Matched Auth"
		name = register_server(client, auth.group(1))
		if name:
			print("Server Registered for: " + name)
			server.send_message(client, '{"result": "success"}')
		else:
			print("Auth not recognized!")
			server.send_message(client, '{"result": "failed"}')
	else:
		if(client['can_send']):
			print("Client(%d) said: %s" % (client['id'], message))
			server.send_message_to_token(client['token'], message)


PORT = ws_config['server']['port']
HOST = ws_config['server']['host']
server = WebsocketServer(PORT, host=HOST)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
