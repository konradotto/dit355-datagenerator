from datagenerator.requestgenerator import overpass_handler
import sys
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ifile', help='specify file to load coordinate-seeds from')
    parser.add_argument('-b', '--broker', help='specify ip address of the broker')
    parser.add_argument('-t', '--topic', help='set the topic to which the travel requests are published')
    parser.add_argument('-c', '--client', help='set a name for the mqtt client')
    parser.add_argument('-d', '--device', help='set the device ID for this data generator [int]', type=int)
    parser.add_argument('-p', '--print', help='print all produced json-messages', action='store_true')
    parser.add_argument('-s', '--sleep', help='set the time (in seconds) the emitter sleeps between publishing '
                                              'two consecutive requests[float]', type=float)
    parser.add_argument('-o', '--offset', help='set the uncertainty of coordinate seeds in meters [float]', type=float)
    parser.add_argument('-l', '--limit', help='limit the number of coordinate seeds used by this data generator',
                        type=int)

    parser.parse_args()
    overpass_handler.run(sys.argv[1:])
