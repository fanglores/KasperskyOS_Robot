import socket
import rapidjson
import sys
import netifaces

# Create a TCP/IP socket

from pydantic import BaseModel, conint, confloat


"""  DataSchema  """


class EngineCommandSchema(BaseModel):
    type_engine: str
    speed: conint(ge=-100, le=100)
    time: confloat(gt=0)

""" ANSWER ROBOT """
def result_answer(code_answer):
    if code_answer == 0:
        return "GOOD", 200
    elif code_answer == 1: #ощибка в двигателях
        return "BAD_ENGINE", 301
    elif code_answer == 2: #ошибка в принятии команды
        return "BAD_COMMAND", 302


def send_command(new_commands: EngineCommandSchema, IP_CONFIG):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', 5000)

    while True:
        try:
            sock.connect(server_address)

            """send command"""
            res = new_commands.dict()
            res = rapidjson.dumps(res)
            res = str(res)
            res = res.encode('UTF-8')
            sock.send(res)
            get_answer = sock.recv(16)

            res_answer = int(chr(get_answer[0]))

            sock.close()
            return result_answer(res_answer)

        except ConnectionRefusedError:
            print("[SYSTEM NETWORK] ~ ", 'ERR0R CONNECT CLIENT', 404)
            print("[SYSTEM NETWORK] ~ RECONNECT ROBOT")

def find_my_ip(ip_config):
    interfaces = netifaces.interfaces()
    for i in interfaces:
        if i == 'lo':
            continue
        iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
        if iface != None:
            iter = 0
            for j in iface:
                print(j['addr'])
                if iter == 0:
                    ip_config = j['addr']
                    break
                iter += 1
            break

    return ip_config

# tyt = {"type_engine":"tank","speed":1.0,"time":1.0}
# print(send_command(EngineCommandSchema(**tyt), "0.0.0.0"))