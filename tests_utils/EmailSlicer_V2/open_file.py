import pkgutil
import os
import encodings

def all_encodings():
    modnames = set(
        [modname for importer, modname, ispkg in pkgutil.walk_packages(
            path=[os.path.dirname(encodings.__file__)], prefix='')])
    aliases = set(encodings.aliases.aliases.values())
    return modnames.union(aliases)

if __name__ == "__main__":
    file = '/home/nogueira/Documents/EmailSlicer/EmailSlicer_V2/output_files/ipleiria/Ficheiro de Dados do Outlook/Itens eliminados/5.eml'

    aux = -1
    encoding_lsit = ['utf-8', 'windows-1252']
    encodings = all_encodings()
    for enc in encoding_lsit:
        try:
            with open(file, encoding=enc) as f:
                for line in f:
                    print(line)
            aux = 0            
        except:
            print('ERROR')
        finally:
            if aux == 0:
                exit(aux)