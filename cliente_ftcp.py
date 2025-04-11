import socket
from sys import argv, exit

MAX_FILE_SIZE = 10240
SERVER_IP = "127.0.0.1"
UDP_PORT = 5698  # Alterar posteriormente


def start_negotiation(requested_file: str) -> dict:
    """
    Envia uma requisição (via UDP) para o servidor, solicitando um determinado
    arquivo.

    Parameters
    ----------
    requested_file : str
        O nome do arquivo solicitado.

    Returns
    -------
    dict
        Retorna um mapa contendo as informações retornadas pelo servidor. Caso
        a negociação falhe, uma exceção é lançada informando o erro ocorrido.
    """

    server_address = (SERVER_IP, UDP_PORT)
    req_template = "REQUEST,UDP,{file}"

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        request = req_template.format(file=requested_file)
        udp_socket.sendto(request.encode("utf-8"), server_address)
        data, _ = udp_socket.recvfrom(1024)

    response = parse_response(data)

    if response.get("FAILED"):
        print(response.get("ERROR_MSG"))
        exit(1)

    return response


def transfer_file_over_tcp(request_data: dict) -> tuple[str, int]:
    """
    Solicita a transferência (via TCP) do arquivo indicado na negociação inicial
    para o servidor. Ao término da transferência, envia um ACK para o servidor
    com o número de bytes recebido, encerrando a conexão.

    Parameters
    ----------
    request_data : dict
        Um mapa com as informações retornadas da negociação inicial com o
        servidor.

    Returns
    -------
    tuple[str, int]
        Uma tupla contendo o nome do arquivo e seu tamanho em bytes.
    """

    socket_port = request_data.get("SOCKET_PORT")
    filename = request_data.get("FILENAME")

    server_address = (SERVER_IP, socket_port)
    received_bytes = 0
    req_template = "get,{file}"
    ack_template = "ftcp_ack,{bytes}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        print(f"Connecting to server at {SERVER_IP}:{socket_port}...")
        tcp_socket.connect(server_address)

        request = req_template.format(file=filename)
        tcp_socket.sendall(request.encode("utf-8"))
        response = tcp_socket.recv(MAX_FILE_SIZE)

        received_bytes = len(response)
        ack = ack_template.format(bytes=received_bytes)
        tcp_socket.sendall(ack.encode("utf-8"))
    
    return filename, received_bytes


def parse_response(data: bytes) -> dict:
    """
    Extrai as informações da resposta do servidor.

    Parameters
    ----------
    data : bytes
        Os dados de uma resposta do servidor.

    Returns
    -------
    dict
        Um mapa contendo as informações da requisição. Contém os seguintes
        campos:

        - PROTOCOL (str): o protocolo indicado para a transferência do arquivo
        - FAILED (bool): flag que indica se a requisição falhou
        - SOCKET_PORT (int): a porta do socket para a transferência do arquivo
        - FILENAME (str): o nome do arquivo solicitado
        - ERROR_MSG (str): mensagem de erro retornada pelo servidor, em caso de 
          falhas

        Para requisições válidas, o campo ERROR_MSG terá valor "None".

        Para requisições inválidas, os campos PROTOCOL, FILENAME e SOCKET_PORT
        terão valor "None".
    """

    res_data = {
        "FAILED": False,
        "SOCKET_PORT": None,
        "PROTOCOL": None,
        "FILENAME": None,
        "ERROR_MSG": None,
    }

    decoded_data = data.decode().split(",")
    command, *fields = decoded_data
    if command == "ERROR":
        res_data["FAILED"] = True
        res_data["ERROR_MSG"] = fields[0]
    else:
        res_data["PROTOCOL"], res_data["SOCKET_PORT"], res_data["FILENAME"] = decoded_data

    return res_data


if __name__ == "__main__":
    if len(argv) != 2:
        print("Uso: python3 client_ftcp.py [ARQUIVO]")
        exit(1)

    requested_file = argv[1]
    response = start_negotiation(requested_file)
    file, byte_count = transfer_file_over_tcp(requested_file, response)

    print(f"File {file} ({byte_count} B) received successfully!")
