

class Obj(object):
    def __init__(self, filename):
        with open(filename, "r") as file:
            self.lines = file.read().splitlines()

        self.vertices = []
        self.texCoords = []
        self.normals = []
        self.faces = []

        for i in range (len(self.lines)):
            line = self.lines[i]
            try:
                prefix, value = line.split(" ", 1)
                value = value.lstrip(" ").rstrip(" ")
            except:
                continue
                
            if prefix == "v":
                self.vertices.append(list(map(float, filter(lambda x: x != '', value.split(" ")))))
            elif prefix == "vt":
                self.texCoords.append(list(map(float, value.split(" "))))
            elif prefix == "vn":
                if (value[-1] == '\\'):
                    value = value.replace('\\', "")
                    value += self.lines[i + 1].lstrip(" ")
                    
                self.normals.append(list(map(float, value.split(" "))))
            elif prefix == "f":
                if (value[-1] == '\\'):
                    value = value.replace('\\', "")
                    value += self.lines[i + 1].lstrip(" ")
                try:
                    self.faces.append([list(map(int, vert.split("/"))) for vert in value.split(" ")])
                
                except ValueError:
                    self.faces.append([list(map(lambda x: int(x) if x else 0, vert.split("/"))) for vert in value.split(" ")])

    
