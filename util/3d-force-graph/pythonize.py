with open("pythonized.out","w+") as out_f:
    with open("index.html") as f:
        lines = f.readlines()
        for line in lines:
            print(line.__repr__())
            out_f.write(line.__repr__()+",\n")
