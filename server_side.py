import socket 
import threading

def handle_tcp_client(conn, addr):
    print(f"TCP Client connected from {addr}")
    
    with conn:
        data = conn.recv(1024)

        while not data:
            print(data.decode('utf-8'))
            conn.sendall(data)
            data = conn.recv(1024)
    
    print(f"TCP Client disconnected from {addr}")

def tcp_protocol():
    """
    Cria uma thread para cada cliente que estabelece uma conexão com o servidor.
    """

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(('0.0.0.0', 6000)) # TODO, change to read the config data from an 'ini' file
    tcp_sock.listen(5)

    while True:
        conn, addr = tcp_sock.accept()
        client_thread = threading.Thread(target=handle_tcp_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()

def udp_protocol():
    pass

def init_protocol(method):
    """
    Inicia uma thread que vai executar um método relacionado ao protocolo
    de interesse

    Parameter
    ---------
    method:
        uma referência ao método relacionado a um método.
    """

    protocol_thread = threading.Thread(target=method)
    protocol_thread.daemon = True
    protocol_thread.start()

def main():
    init_protocol(udp_protocol)
    init_protocol(tcp_protocol)
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServidor Encerrado.")


if __name__ == "__main__":
    main()
