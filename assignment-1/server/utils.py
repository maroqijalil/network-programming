import os


def handle_send_file(socket, command) -> None:
  commands = command.decode('utf-8').split(" ")
  file_name = commands[1][:-1]
  file_path = os.path.dirname(__file__) + "/dataset/" + file_name

  state = False
  data = b''

  if os.path.exists(file_path):
    file_size = os.path.getsize(file_path)

    data = (f'\nfile-name: {file_name},\nfile-size: {file_size},\n\n\n').encode('utf-8')

    with open(file_path, 'rb') as file:
      data += file.read()

      state = True
  
  if state:
    socket.sendall(data)

  else:
    if len(data):
      socket.send(b'file exists but there is someting goes wrong, please try again!')

    else:
      socket.send(b'file doesn\'t exist')
