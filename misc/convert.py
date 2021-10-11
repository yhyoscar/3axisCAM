import os 


def add_window_linebreak(fin, fout):
    x = open(fin, 'rb').read()
    fid = open(fout, 'wb')
    newx = x.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    #newx = b'M3 S1000\r\n' + newx + b'\r\nM05\r\nM02'
    fid.write(newx)
    print(fin, len(x), '->', fout, len(newx))
    return 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, default=None, 
                        help="input file")
    parser.add_argument("-o", "--output", type=str, required=True, default=None, 
                        help="output file")
    args = parser.parse_args()

    add_window_linebreak(args.input, args.output)
