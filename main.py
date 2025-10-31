import xml.etree.ElementTree as ET
import base64
import os, sys

def main(path, outdir):
    tree = ET.parse(path)
    root = tree.getroot()

    for item in root:
        if item.tag == 'item':
            path_elem = item.find('path')
            if path_elem is not None:
                path = path_elem.text
            else:
                continue
            ext_elem = item.find('extension')
            extension = ext_elem.text if ext_elem is not None else 'null'
            mime_elem = item.find('mimetype')
            mimetype = mime_elem.text if mime_elem is not None else ''
            resp_elem = item.find('response')
            if resp_elem is not None and resp_elem.text:
                response_bytes = base64.b64decode(resp_elem.text)
                # find body
                header_end = response_bytes.find(b'\r\n\r\n')
                if header_end == -1:
                    header_end = response_bytes.find(b'\n\n')
                if header_end != -1:
                    if response_bytes[header_end:header_end+4] == b'\r\n\r\n':
                        body = response_bytes[header_end + 4:]
                    else:
                        body = response_bytes[header_end + 2:]
                else:
                    body = response_bytes
                # process path
                if '?' in path:
                    path = path.split('?')[0]
                if path == '/':
                    if mimetype.upper() == 'HTML':
                        path = '/index.html'
                    else:
                        path = '/index'  # fallback
                file_path = path.lstrip('/')
                dir_path = os.path.dirname(file_path)
                if dir_path:
                    os.makedirs(os.path.join(outdir, dir_path), exist_ok=True)
                with open(os.path.join(outdir, file_path), 'wb') as f:
                    f.write(body)


def usage():
    print("Usage: python main.py <input_file> <output_directory>")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
    else:
        main(sys.argv[1], sys.argv[2])
