class Reply:
  def __init__(self, code = 500, message = "Command unrecognized.") -> None:
    self.code = code
    self.message = message
  
  def get(self) -> str:
    return f'{self.code} {self.message}\r\n'


class Config:
  def __init__(self, filepath) -> None:
    self.filepath = filepath
  
  def get(self) -> dict:
    contents = ''
    with open(self.filepath, 'r') as file:
      contents = file.read()

    config = {}
    if contents != '':
      for line in contents.splitlines():
        if len(line):

          items = line.split('=')

          if len(items) > 1:
            config[items[0]] = items[1]

    else:
      raise Exception("The config isn't found!")

    return config
