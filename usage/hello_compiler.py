import json
import os

from boa.compiler import Compiler


def hello_compiler():
    avm_path = os.path.join(os.getcwd(), 'hello_compiler.avm')
    with open(avm_path, 'w'):
        pass
    Compiler.load_and_save(avm_path)
    json_path = os.path.join(os.getcwd(), 'hello_compiler.debug.json')
    with open(avm_path, 'r') as f:
        avm = f.read()
        print("avm: " + avm)
    with open(json_path, 'r') as f:
        debug_json = json.load(f)
        print("debug_json: " + str(debug_json))
    os.remove(avm_path)
    os.remove(json_path)


if __name__ == '__main__':
    hello_compiler()
