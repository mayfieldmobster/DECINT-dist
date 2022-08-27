"""
node
"""

import socket
import random
import time
import ast
import time
from ecdsa import SigningKey, VerifyingKey, SECP112r2
import asyncio
import os
import json

__version__ = "1.0"


# recieve from nodes
def receive():
    """
    message is split into array the first value the type of message the second value is the message
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 1379))
    server.listen()
    while True:
        try:
            client, address = server.accept()
            message = client.recv(2048).decode("utf-8")#.split(" ")
            server.close()
            return message, address
        except Exception as e:
            print(e)


# send to node
def send(host, message, port=1379, send_all=False):
    """
    sends a message to the given host
    tries the default port and if it doesn't work search for actual port
    this process is skipped if send to all for speed
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
    try:
        client.connect((host, port))
        client.send(message.encode("utf-8"))
        print(f"Message to {host} {message}\n")
        return
    except ConnectionRefusedError:
        if not send_all:
            try:
                with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
                    nodes = json.load(file)
                for node in nodes:
                    if node["ip"] == host:
                        if not int(node["port"]) == 1379:
                            client.connect((host, int(node["port"])))
                            client.send(message.encode("utf-8"))
                            # print(f"Message to {host} {message}\n")
                            return
            except ConnectionRefusedError:
                return "node offline"

async def async_send(host, message, port=1379, send_all=False):
    """
    sends a message to the given host
    tries the default port and if it doesn't work search for actual port
    this process is skipped if send to all for speed
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP

    try:
        client.connect((host, port))
        client.send(message.encode("utf-8"))
        print(f"Message to {host} {message}\n")
        return
    except Exception as e:
        if not send_all:
            if isinstance(e, ConnectionRefusedError):
                try:
                    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
                        nodes = json.load(file)
                    for node in nodes:
                        if node[1] == host:
                            if not int(node["port"]) == 1379:
                                client.connect((host, int(node["port"])))
                                client.send(message.encode("utf-8"))
                                print(f"Message to {host} {message}\n")
                                return
                except Exception as e:
                    return "node offline"

# check if nodes online
def online(address):
    """
    asks if a node is online and if it is it returns yh
    """
    print(address)
    # socket.setdefaulttimeout(1.0)
    try:
        send(address, "ONLINE?")
        return True
    except Exception as e:
        # socket.setdefaulttimeout(3.0)
        print(e)
        return False

def rand_act_node(num_nodes=1):
    """
    returns a list of random active nodes which is x length
    """
    with open(f"{os.path.dirname(__file__)}/info/Public_key.txt", "r") as file:
        key = file.read()
    nodes = []
    i = 0
    while i != num_nodes:  # turn into for loop
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
            all_nodes = json.load(file)
        me = socket.gethostbyname(socket.gethostname())
        node_index = random.randint(0, len(all_nodes) - 1)
        node = all_nodes[node_index]
        #print(node)
        if node["pub_key"] == key or node["ip"] == me:
            continue
        alive = online(node["ip"])
        if alive:
            nodes.append(node)
            i += 1

    if len(nodes) == 1:
        return nodes[0]
    else:
        return nodes


def request_reader(type, ip="192.168.68.1"):
    """
    reads the recent messages and returns the message of the requested type
    """
    with open("recent_messages.txt", "r") as file:
        lines = file.read().splitlines()
    nreq_protocol = ["NREQ"]  # node request
    yh_protocol = ["yh"]
    trans_protocol = ["TRANS"]
    breq_protocol = ["BREQ"]
    pre_protocol = ["ONLINE?", "GET_NODES", "BLOCKCHAIN?"]
    node_lines = []
    nreq_lines = []
    yh_lines = []
    trans_lines = []
    breq_lines = []
    online_lines = []
    if str(lines) != "[]":
        for line in lines:
            line = line.split(" ")

            if line[0] == "" or line[0] == "\n":
                lines.remove(line)  # delete blank lines

            elif line[1] in nreq_protocol:
                nreq_lines.append(" ".join(line))

            elif line[1] in yh_protocol and line[0] == ip:
                yh_lines.append(" ".join(line))

            elif line[1] in trans_protocol:
                trans_lines.append(" ".join(line))

            elif line[1] in pre_protocol:
                online_lines.append(" ".join(line))

            elif line[1] in breq_protocol:
                breq_lines.append(" ".join(line))

            else:
                node_lines.append(" ".join(line))

        if type == "YH":
            if len(yh_lines) != 0:
                new_lines = []
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "r") as file:
                    file_lines = file.readlines()
                for f_line in file_lines:
                    f_line.split(" ")
                    if not yh_lines[0] in f_line:
                        if not f_line.strip("\n") == "":
                            new_lines.append(f_line)
                open(f"{os.path.dirname(__file__)}/recent_messages.txt", "w").close()
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a") as file:
                    for n_line in new_lines:
                        file.write(n_line)
            return yh_lines

        elif type == "NODE":
            if len(node_lines) != 0:
                new_lines = []
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "r") as file:
                    file_lines = file.readlines()
                for f_line in file_lines:
                    f_line.split(" ")
                    if not node_lines[0] in f_line:
                        if not f_line.strip("\n") == "":
                            new_lines.append(f_line)
                open(f"{os.path.dirname(__file__)}/recent_messages.txt", "w").close()
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a") as file:
                    for n_line in new_lines:
                        file.write(n_line)
            return node_lines

        elif type == "NREQ":
            if len(nreq_lines) != 0:
                new_lines = []
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "r+") as file:
                    file_lines = file.readlines()
                for f_line in file_lines:
                    f_line.split(" ")
                    if not nreq_lines[0] in f_line:
                        if not f_line.strip("\n") == "":
                            new_lines.append(f_line)
                open(f"{os.path.dirname(__file__)}/recent_messages.txt", "w").close()
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a") as file:
                    for n_line in new_lines:
                        file.write(n_line)
            return nreq_lines

        elif type == "ONLINE":
            if len(online_lines) != 0:
                new_lines = []
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "r+") as file:
                    file_lines = file.readlines()
                for f_line in file_lines:
                    f_line.split(" ")
                    if not online_lines[0] in f_line:
                        if not f_line.strip("\n") == "":
                            new_lines.append(f_line)
                open(f"{os.path.dirname(__file__)}/recent_messages.txt", "w").close()
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a") as file:
                    for n_line in new_lines:
                        file.write(n_line)
            return online_lines

        elif type == "TRANS":
            if len(trans_lines) != 0:
                new_lines = []
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "r") as file:
                    file_lines = file.readlines()
                for f_line in file_lines:
                    if not trans_lines[0] in f_line:  # update to check multiple lines to lazy to do rn
                        if not f_line.strip("\n") == "":
                            new_lines.append(f_line)
                open(f"{os.path.dirname(__file__)}/recent_messages.txt", "w").close()
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a") as file:
                    for n_line in new_lines:
                        file.write(n_line)
            return trans_lines

        elif type == "BREQ":
            if len(breq_lines) != 0:
                new_lines = []
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "r") as file:
                    file_lines = file.readlines()
                for f_line in file_lines:
                    if not breq_lines[0] in f_line:  # update to check multiple lines to lazy to do rn
                        if not f_line.strip("\n") == "":
                            new_lines.append(f_line)
                open(f"{os.path.dirname(__file__)}/recent_messages.txt", "w").close()
                with open(f"{os.path.dirname(__file__)}/recent_messages.txt", "a") as file:
                    for n_line in new_lines:
                        file.write(n_line)
            return breq_lines


async def send_to_all(message):
    """
    sends to all nodes
    """
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        all_nodes = json.load(file)
    for f in asyncio.as_completed([async_send(node_["ip"], message, port=node_["port"], send_all=True) for node_ in all_nodes]):
        result = await f

async def send_to_all_no_dist(message):
    """
    sends to all nodes
    """
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        all_nodes = json.load(file)
    for f in asyncio.as_completed([async_send(node_["ip"], message, port=node_["port"], send_all=True) for node_ in all_nodes if node_["node_type"]!="dist"]):
        result = await f

def announce(pub_key, port, version, node_type, priv_key):
    announcement_time = str(time.time())
    if not isinstance(priv_key, bytes):
        priv_key = SigningKey.from_string(bytes.fromhex(priv_key), curve=SECP112r2)
    sig = str(priv_key.sign(announcement_time.encode()).hex())
    print(f"HELLO {announcement_time} {pub_key} {str(port)} {version} {node_type} {sig}")
    asyncio.run(send_to_all(f"HELLO {announcement_time} {pub_key} {str(port)} {version} {node_type} {sig}"))


def update(old_key, port, version, priv_key, new_key=None):
    if not new_key:
        new_key = old_key
    update_time = str(time.time())
    if not isinstance(priv_key, bytes):
        priv_key = SigningKey.from_string(bytes.fromhex(priv_key), curve=SECP112r2)
    sig = str(priv_key.sign(update_time.encode()).hex())
    asyncio.run(send_to_all(f"UPDATE {update_time} {old_key} {new_key} {str(port)} {version} {sig}"))
    with open(f"{os.path.dirname(__file__)}/info/Public_key.txt", "w") as file:
        file.write(new_key)


def delete(pub_key, priv_key):
    update_time = str(time.time())
    if not isinstance(priv_key, bytes):
        priv_key = SigningKey.from_string(bytes.fromhex(priv_key), curve=SECP112r2)
    sig = str(priv_key.sign(update_time.encode()).hex())
    asyncio.run(send_to_all(f"DELETE {update_time} {pub_key} {sig}"))


def get_nodes():
    print("---GETTING NODES---")
    node = rand_act_node()
    time.sleep(0.1)
    send(node["ip"], "GET_NODES")
    tries = 0
    while tries < 10:
        time.sleep(5)
        lines = request_reader("NREQ")
        if lines:
            for line in lines:
                print(f"NODE LINE: {line}")
                line = line.split(" ")
                nodes = line[2]
                nodes = ast.literal_eval(nodes)
                if line[0] == node["ip"]:
                    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "w") as file:
                        json.dump(nodes, file)
                    print("---NODES RECEIVED---")
                    print("NODES UPDATED SUCCESSFULLY")
                    return
        else:
            tries += 1
            continue


def send_node(host):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        Nodes = json.load(file)
    str_node = str(Nodes)
    str_node = str_node.replace(" ", "")
    send(host, "NREQ " + str_node)


def new_node(initiation_time, ip, pub_key, port, node_version, node_type, sig):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    public_key = VerifyingKey.from_string(bytes.fromhex(pub_key), curve=SECP112r2)
    if public_key.verify(bytes.fromhex(sig), str(initiation_time).encode()):
        new_node = {"time": initiation_time, "ip": ip, "pub_key": pub_key, "port": port, "version": node_version,
                    "node_type": node_type}
        for node in nodes:
            if node["pub_key"] == pub_key:
                return
            if node["ip"] == ip:
                return
        nodes.append(new_node)
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "w") as file:
            json.dump(nodes, file)
        print("---NODE ADDED---")
    else:
        return "node invalid"


def update_node(ip, update_time, old_key, new_key, port, node_version, sig):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    public_key = VerifyingKey.from_string(bytes.fromhex(old_key), curve=SECP112r2)
    try:
        assert public_key.verify(bytes.fromhex(sig), str(update_time).encode())
        for node in nodes:
            if node["ip"] == ip:
                node["pub_key"] = new_key
                node["port"] = port
                node["version"] = node_version
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "w") as file:
            json.dump(nodes, file)
            print("NODE UPDATED")
    except:
        return "update invalid"


def delete_node(deletion_time, ip, pub_key, sig):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    public_key = VerifyingKey.from_string(bytes.fromhex(pub_key), curve=SECP112r2)
    try:
        assert public_key.verify(bytes.fromhex(sig), str(deletion_time).encode())
        for node in nodes:
            if node["ip"] == ip and node["pub_key"] == pub_key:
                nodes.remove(node)
        with open(f"{os.path.dirname(__file__)}/info/nodes.json", "w") as file:
            json.dump(nodes, file)
    except:
        return "cancel invalid"



def version_update(ip, ver):
    with open(f"{os.path.dirname(__file__)}/info/nodes.json", "r") as file:
        nodes = json.load(file)
    for nod in nodes:
        if nod["ip"] == ip:
            nod["version"] = ver
            break


class NodeError(Exception):
    pass


class UnrecognisedCommand(NodeError):
    pass


class ValueTypeError(NodeError):
    pass


class UnrecognisedArg(NodeError):
    pass

def check_float(value):
    try:
        float(value)
        if float(value) < 0:
            raise ValueTypeError
        if value.isdigit():
            raise ValueTypeError
        return True
    except ValueError:
        return False


def check_int(value):
    if value.isdigit():
        return True
    else:
        return False


#  TODO add AI_JOB protocols
def message_handler(message):
    """
    All messages are in the form of "<ip> PROTOCOL <args...>"

    HELLO <ip> <port> <pub_key> <version> <node_type> <signature>
    UPDATE <ip> <update_time> <old_key> <new_key> <port> <version> <signature>
    DELETE <ip> <deletion_time> <public_key> <signature>
    GET_NODES <ip>
    NREQ <ip> <nodes>
    BLOCKCHAIN? <ip>
    BREQ <ip> <blockchain>
    VALID <ip> <block_index> <validation_time>
    TRANS_INVALID <block_index> <transaction_index>
    TRANS <ip> <transaction_time> <sender_public_key> <recipient_public_key> <transaction_value> <signature>
    STAKE <ip> <staking_time> <public_key> <stake_value> <signature>
    UNSTAKE <ip> <unstaking_time> <public_key> <unstake_value> <signature>
    ONLINE? <ip>
    ERROR <ip> <error_message>
    BLOCKCHAINLEN? <ip>
    BLENREQ <ip> <number_of_chunks>
    """
    try:
        if isinstance(message, str):
            message = message.split(" ")
        protocol = message[1]
    except IndexError:
        raise UnrecognisedArg("No Protocol Found")

    node_types = ["Lite", "Blockchain", "AI", "dist"]

    if protocol == "GET_NODES":
        if len(message) != 2:
            raise UnrecognisedArg(f"number of args given incorrect during {protocol}")

    elif protocol == "HELLO":
        # host, HELLO, announcement_time, public key, port, version, node type, sig
        if len(message) != 8:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Public Key is the wrong size")

        if not check_int(message[4]):
            raise ValueTypeError("port not given as int")
        else:
            port = int(message[4])

        if not port > 0 and port < 65535:
            raise ValueTypeError("TCP port out of range")

        if not check_float(message[5]):
            raise ValueTypeError("version not given as float")

        if message[6] not in node_types:
            raise UnrecognisedArg("Node Type Unknown")

        if len(message[7]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "VALID":
        # host, VALID , block index, time of validation, block
        return # just for testing
        if len(message) != 5:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_int(message[2]):
            raise ValueTypeError("Block Index not given as int")

        if not check_float(message[3]):
            raise ValueTypeError("time not given as float")

        try:
            ast.literal_eval(message[4])
        except:
            raise ValueTypeError("BLock is not given as block")

    elif protocol == "TRANS_INVALID":
        # host, TRANS_INVALID, Block Index, Transaction invalid
        if len(message) != 4:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_int(message[2]):
            raise ValueTypeError("Block Index not given as int")

        if not check_int(message[3]):
            raise ValueTypeError("Transaction Index not given as int")

    elif protocol == "ONLINE?":
        # host, ONLINE?
        if len(message) != 2:
            raise UnrecognisedArg("number of args given incorrect")

    elif protocol == "BLOCKCHAIN?":
        # host, BLOCKCHAIN?
        if len(message) != 3:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_int(message[2]):
            raise ValueTypeError("Chunk Index not given as int")

    elif protocol == "UPDATE":
        # host, UPDATE, update time, old public key, new public key, port, version, sig
        if len(message) != 7:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Old Public Key is the wrong size")

        if len(message[4]) != 56:
            raise UnrecognisedArg("New Public Key is the wrong size")

        if not check_int(message[5]):
            raise ValueTypeError("port not given as int")
        else:
            port = int(message[5])

        if not port >= 0 and port < 65535:
            raise ValueTypeError("TCP port out of range")

        if not check_float(message[6]):
            raise ValueTypeError("version not given as float")

        if len(message[7]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "DELETE":
        # host, DELETE, time, public key, sig
        if len(message) != 5:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Public Key is the wrong size")

        if len(message[4]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "BREQ":
        # host, BREQ, blockchain
        try:
            ast.literal_eval(message[2])
        except ValueError:
            raise ValueTypeError("Blockchain not given as Blockchain")

    elif protocol == "NREQ":
        # host, NREQ, nodes
        try:
            ast.literal_eval(message[2])
        except ValueError:
            raise ValueTypeError("Blockchain not given as Node List")

    elif protocol == "TRANS":
        # host, TRANS, time of transaction, sender public key, receiver public key, amount sent, sig
        if len(message) != 7:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Senders Public Key is the wrong size")

        if len(message[4]) != 56:
            raise UnrecognisedArg("Receivers Public Key is the wrong size")

        if not check_float(message[5]):
            raise ValueTypeError("Amount not given as float")

        if len(message[6]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "ERROR":
        pass

    elif protocol == "yh":
        pass

    elif protocol == "STAKE":
        # host, STAKE, time of stake, public key, amount, sig
        if len(message) != 6:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Public Key is the wrong size")

        if not check_float(message[4]):
            raise ValueTypeError("Stake value not given as float")

        if len(message[5]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "UNSTAKE":
        if len(message) != 6:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_float(message[2]):
            raise ValueTypeError("time not given as float")

        if len(message[3]) != 56:
            raise UnrecognisedArg("Public Key is the wrong size")

        if not check_float(message[4]):
            raise ValueTypeError("Unstake value not given as float")

        if len(message[5]) != 56:
            raise UnrecognisedArg("Signature is the wrong size")

    elif protocol == "BLOCKCHAINLEN?":
        if len(message) != 2:
            raise UnrecognisedArg("number of args given incorrect")

    elif protocol == "BLENREQ":
        if len(message) != 3:
            raise UnrecognisedArg("number of args given incorrect")

        if not check_int(message[2]):
            raise ValueTypeError("Blockchain length not given as int")

    else:
        raise UnrecognisedCommand("protocol unrecognised")
