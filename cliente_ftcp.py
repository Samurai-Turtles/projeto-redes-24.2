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
    request_msg = f"REQUEST,UDP,{requested_file}"

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.sendto(request_msg.encode("utf-8"), server_address)
        data, _ = udp_socket.recvfrom(1024)

    response = parse_response(data)

    if response.get("FAILED"):
        print(response.get("ERROR_MSG"))
        exit(1)

    return response


def download_file_over_tcp(filename: str, response: str):
    """
    Este passo é dividido em quatro etapas:

    1. Cliente estabelece conexão com o servidor TCP
    2. Cliente solicita o arquivo para transferência
    3. Servidor transfere o arquivo solicitado
    4. Cliente verifica o tamanho da arquivo e retorna um ACK para o servidor
    """
    # Estabelecimento de Conexão
    split_response = response.split(",")
    tcp_port = int(split_response[-2])

    server_address = (SERVER_IP, tcp_port)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(server_address)
    print(f"Connected to server at {SERVER_IP}:{tcp_port}")

    # Solicitação do Arquivo
    file_request = f"get,{filename}"
    tcp_socket.sendall(file_request.encode("utf-8"))

    # Envio dos Dados
    response = tcp_socket.recv(MAX_FILE_SIZE)

    # Confirmação pelo Cliente (ACK)
    num_bytes = MAX_FILE_SIZE  # TODO: somehow calculate the file size
    ack = f"ftcp_ack,{num_bytes}"
    tcp_socket.sendall(ack.encode("utf-8"))

    # Encerramento da Conexão
    tcp_socket.close()


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
    requested_file = argv[1]  # TODO: add argument amount validation?
    response = start_negotiation(requested_file)
    download_file_over_tcp(requested_file, response)
