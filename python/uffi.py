import socket
import os
import json
import subprocess
import sys





class ForiegnFunction:
    def __init__(self, cmd: str):
        self.cmd = cmd
    

    def __call__(self, *args, **kwargs):
        pid = os.getpid()
        socket_path = f'/tmp/uffi_{pid}.sock'
        try:
            os.unlink(socket_path)
        except OSError:
            if os.path.exists(socket_path):
                raise
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(socket_path)

        # spawn command
        json = self.prepare_args(*args)
        command = [self.cmd] + list(map(lambda x: str(x), args))
        env = os.environ.copy()
        env['UFFI_SOCKET'] = socket_path
        env['UFFI_ARGS'] = json
        #print(command)
        subprocess.Popen(command, env=env)
        #print(f'Waiting for connection on {socket_path}')

        server.listen(1)
        conn, addr = server.accept()
        
        try:
            #print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                return self.decode_json(data)
        finally:
            conn.close()
            server.close()
            os.unlink(socket_path)


    def prepare_args(self, *args):
        return json.dumps(args)
    
    def decode_json(self, data):
        return json.loads(data)



def get_arguments() -> list:
    if 'UFFI_ARGS' in os.environ:
        return json.loads(os.environ['UFFI_ARGS'])
    else:
        return sys.argv[1:]


def return_uffi(arg):
    data = json.dumps(arg)
    env = os.environ.copy()
    socket_path = env['UFFI_SOCKET']
    #print(f'Sending data to {socket_path}')
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    connected = False
    while not connected:
        try:
            #print(socket_path)
            client.connect(socket_path)
            connected = True
        except:
            pass
    
    client.sendall(bytes(data, 'utf-8'))
    
    client.close()

    exit(0)
