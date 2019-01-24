from preprocessing.download_and_convert_birdify import _download_and_convert_to_spectro, _convert_spectrograms_to_tfrecords
from optparse import OptionParser


def setup_options():
    parser = OptionParser()
    parser.add_option("-f","--file", action="store", type="string", dest="birdifile", help='If file is given, the birdsounds will be fetched by the given URL'
                                                                                            ' in the file.If file is not given, the script fetches the sounds ' 
                                                                                            'of all the bird species (existing on xeno-canto)')
    parser.add_option("-t","--train", action="store", type="int", dest="train", help='Number of data in one training tfrecord. Default value = 5000')
    parser.add_option("-v","--validation", action="store", type="int", dest="validation", help='Number of data in one validation tfrecord. Default value = 500')
    parser.add_option("-d","--directory", action="store", type="string", dest="directory", help='The destination directory, in which tfrecords will be stored.')
    options, _ = parser.parse_args()
    return options

if __name__ == "__main__":
    parser = setup_options()
    if parser.train is None or parser.validation is None:
        train = 5000
        val = 500
    else:
        train = parser.train
        val = parser.validation
    if parser.directory is None:
        directory = "./slim/tmp/birdify"
    else:
        directory = parser.directory

    print('Main :', parser.birdifile)
    _download_and_convert_to_spectro(directory, parser.birdifile)
    _convert_spectrograms_to_tfrecords(directory, train, val)