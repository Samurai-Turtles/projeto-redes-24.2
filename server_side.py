import socket
import threading
import configparser

MAX_FILE_SIZE = 10240
MAX_REQUEST_SIZE = 1024
TCP_PORT = None
UDP_PORT = None
FILES_PATH = "./files/"  # TODO, ler de um config?
FILES = {"FILE_A": None, "FILE_B": None}


def load_config():
    global TCP_PORT, UDP_PORT, FILE_A, FILE_B

    config = configparser.ConfigParser()
    config.read("config.ini")

    TCP_PORT = int(config["SERVER_CONFIG"]["TCP_PORT"])
    UDP_PORT = int(config["SERVER_CONFIG"]["UDP_PORT"])
    FILES["FILE_A"] = config["SERVER_CONFIG"]["FILE_A"]
    FILES["FILE_B"] = config["SERVER_CONFIG"]["FILE_B"]


def process_udp_request(data: bytes):
    """
    Processa uma requisição recebida via UDP, interpretando os dados
    recebidos e formatando uma resposta de acordo com o protocolo definido.

    Parameters
    ----------
    data : bytes
        os dados recebidos do cliente, em formato de bytes. Espera-se
        uma string separada por vírgulas, contendo informações do protocolo.

    Returns
    -------
    str
        uma string formatada com a resposta para o cliente. Caso o protocolo
        recebido seja inválido, uma mensagem
        de erro padrão será retornada.
    """
    converted = data.decode("utf-8").split(",")
    converted[-1] = converted[-1].strip()
    out = f"RESPONSE,TCP,{TCP_PORT},{converted[-1]}"

    if "UDP" in converted:
        out = "ERROR,PROTOCOLO INVALIDO,,"

    if not (converted[-1] in FILES.values()):
        out = "ERROR,ARQUIVO INEXISTENTE,,"

    return out


def process_tcp_request(data: bytes):
    converted = data.decode().split(",")
    converted[-1] = converted[-1].strip()
    out = None

    if converted[0] != "get":
        return out

    with open(f"{FILES_PATH}{converted[-1]}", 'rb') as file:
        out = file.read()

    return out


def handle_tcp_client(conn, addr):
    print(f"TCP Client connected from {addr}")

    with conn:
        data = None

        while not data:
            data = conn.recv(MAX_REQUEST_SIZE)

        processed_file = process_tcp_request(data)

        if processed_file != None:
            conn.sendall(processed_file)
            print(f"File sent to {addr}.")

    print(f"TCP Client disconnected from {addr}")


def tcp_protocol():
    """
    Cria uma thread para cada cliente que estabelece uma conexão com o servidor.
    """
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(("0.0.0.0", TCP_PORT))
    tcp_sock.listen(5)

    while True:
        conn, addr = tcp_sock.accept()
        client_thread = threading.Thread(
            target=handle_tcp_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()


def udp_protocol():
    """
    Inicia o servidor UDP que ficará escutando na porta configurada,
    recebendo mensagens e respondendo conforme a lógica do protocolo.
    """
    print(f"UDP Received listening on port {UDP_PORT}")
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(("0.0.0.0", UDP_PORT))

    while True:
        data, addr = udp_sock.recvfrom(MAX_REQUEST_SIZE)

        if not data:
            continue

        protocol_message = data.decode("utf-8")
        print(f"UDP Received from {addr}: {protocol_message}")

        client_request = process_udp_request(data)
        udp_sock.sendto(str.encode(client_request), addr)


def init_protocol(method):
    """
    Inicia uma thread que vai executar um método relacionado ao protocolo
    de interesse

    Parameter
    ---------
    method
        uma referência ao método relacionado a um método.
    """
    protocol_thread = threading.Thread(target=method)
    protocol_thread.daemon = True
    protocol_thread.start()


def main():
    load_config()

    init_protocol(udp_protocol)
    init_protocol(tcp_protocol)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServidor Encerrado.")


if __name__ == "__main__":
    main()
