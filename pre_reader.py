import node




def read():
    print("---ONLINE READER STARTED---")
    while True:
        online_lines = node.request_reader("ONLINE")
        # TODO recombine reader and online reader
        if online_lines:
            for message in online_lines:
                message = message.split(" ")
                try:
                    node.message_handler(message)
                except Exception as e:
                    node.send(message[0], f"ERROR {e}")
                    print(message[1], e)
                    continue
                if message[1] == "ONLINE?":
                    print(f"yh sent to {message[0]}")
                    node.send(message[0], "yh")

                elif message[1] == "GET_NODES":
                    print("GET_NODES")
                    node.send_node(message[0])

if __name__ == "__main__":
    read()