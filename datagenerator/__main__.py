from datagenerator.requestgenerator import overpass_handler
import sys
import argparse

if __name__ == "__main__":
    # Define an argument parser and the options it takes
    # Including the help options that will be printed when using <-h>
    arguments = sys.argv[1:]
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
    parser.add_argument('-f', '--filename', help='specify filename to save logs of the published messages to')
    parser.add_argument('-O', '--days_offset',
                        help='set the number of days a request can be off the current date. Default=7 days',
                        type=float)
    parser.add_argument('-r', '--resend',
                        help='Open a logfile and resend the requests stored in it instead of creating new ones',
                        action='store_true')
    parser.add_argument('-D', '--shift_date', metavar='DAYS',
                        help='shift the date of the produced travel requests into the past '
                             '(negative numbers for shift into the future)', type=float)

    parser.parse_args()

    if ('-r' in arguments) or ('--resend' in arguments):
        overpass_handler.resend_from_logfile(arguments)
    else:
        overpass_handler.run(arguments)
