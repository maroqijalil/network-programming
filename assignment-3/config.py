def get_config(filename: str) -> dict:
  contents = ''
  with open(filename, 'r') as file:
    contents = file.read()
  
  config = {}
  if contents != '':
    is_section = False
    section_name = ''

    for line in contents.splitlines():
      item = line.split()

      if len(item) > 1:
        if item[1] == '{':
          is_section = True
          section_name = item[0]
          config[section_name] = {}
        
        else:
          if is_section:
            config[section_name][item[0]] = item[1]
          
          else:
            config[item[0]] = item[1]
      
      else:
        if item[0] == '}':
          is_section = False

  return config
