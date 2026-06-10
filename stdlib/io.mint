#mode light

fn read(path):
    return read_file(path)

fn write(path, content):
    return write_file(path, content)

fn exists(path):
    return file_exists(path)

fn read_lines(path):
    content = read_file(path)
    return split(content, "\n")

fn write_lines(path, lines):
    content = join(lines, "\n")
    return write_file(path, content)
