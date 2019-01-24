from .sounds.download_birdify_data import FetchData, BirdSound, create_if_directory_not_exists
from .sounds.convert_birdify_to_spectrogram import WavPreprocessor
from .images.convert_birdify_to_tfrecord import run
from inspect import getfile, currentframe
from numpy import arange
from os import listdir, remove, rmdir, walk
from os.path import exists
from shutil import rmtree
from sys import exit


_PATH_OF_THIS_FILE = getfile(currentframe())
_URL_PREFIX = "http://www.xeno-canto.org/api/2/recordings?query="
_URL_SUFIX = "%20q:a"
_URL_IF_EMPTY = "http://www.xeno-canto.org/api/2/recordings?query=q:a"
_PATH_TO_SOUNDS = "./sounds"
_PATH_TO_SPECTRO = "./spectrograms"
_THRESHOLD = 0.02


def _download_and_convert_to_spectro(path_to_tfrecords, path_to_birdifile=None):
    if not exists(path_to_tfrecords):
        fetcher = FetchData()
        spectrogramer = WavPreprocessor()
        if path_to_birdifile is not None:
            if not exists(path_to_birdifile):
                print("%s: File named %s does not exist."%(_PATH_OF_THIS_FILE, path_to_birdifile))
                exit()
            '''
            with open(path_to_birdifile, 'a') as f:
                f.write('\nendoffile')
            '''
            with open(path_to_birdifile) as f:
                create_if_directory_not_exists(_PATH_TO_SOUNDS)
                create_if_directory_not_exists(_PATH_TO_SPECTRO)
                query = f.readline()
                query = query.rstrip('\r')
                query = query.rstrip('\n')
                while "" != query:
                    print(query)
                    url = "%s%s%s"%(_URL_PREFIX, query, _URL_SUFIX)
                    nr_of_pgs = fetcher.get_nr_of_pages(url=url)
                    for i in arange(1, nr_of_pgs+1):
                        new_url = "%s&pg=%d"%(url, i)
                        print(new_url)
                        recordings = fetcher.get_records_by_area(pg_nr=i, url=new_url)
                        list_of_records = fetcher.get_list_of_birdsounds(metadata=recordings)
                        print("length of list of records:", len(list_of_records))
                        if len(list_of_records) > 0:
                            name_of_bird = "%s_%s"%(list_of_records[0].generic_name, list_of_records[0].species_name)
                            path_to_bird_spectro = "%s/%s"%(_PATH_TO_SPECTRO, name_of_bird)
                            print(path_to_bird_spectro)
                            if not exists(path_to_bird_spectro):
                                create_if_directory_not_exists(path_to_bird_spectro)
                                path_to_bird = "%s/%s"%(_PATH_TO_SOUNDS, name_of_bird)
                                create_if_directory_not_exists(path_to_bird)
                                for data in list_of_records:
                                    return_value = fetcher.download_birdsound_if_not_exists(birdsound=data, path=path_to_bird)
                                    if return_value == 0:
                                        path_to_wav = "%s/%s.wav"%(path_to_bird, data.file_name)
                                        name_of_bird_spectro = "%s/%s"%(path_to_bird_spectro,data.file_name)
                                        spectrogramer.perform_save_multiple_spectrograms(224, 224, path_to_wav, name_of_bird_spectro, ".png", _THRESHOLD)
                                        print("Removing %s ..." % (path_to_wav))
                                        remove(path_to_wav)
                                        print("Removing %s has been successful." % (path_to_wav))
                                print("Removing %s ..." % (path_to_bird))
                                rmtree(path_to_bird)
                                print("Removing %s has been successful." % (path_to_bird))
                    query = f.readline()
                    query = query.rstrip('\r')
                    query = query.rstrip('\n')
        else:
            nr_of_pgs = fetcher.get_nr_of_pages(url=_URL_IF_EMPTY)
            for i in arange(nr_of_pgs):
                new_url = "%s&pg=%d"%(_URL_IF_EMPTY, i)
                print("_download_and_convert_to_spectro:", new_url, " ",i)
                recordings = fetcher.get_records_by_area(pg_nr=i, url=new_url)
                list_of_records = fetcher.get_list_of_birdsounds(metadata=recordings)
                for data in list_of_records:
                    name_of_bird = "%s_%s"%(data.generic_name, data.species_name)
                    path_to_bird_spectro = "%s/%s"%(_PATH_TO_SPECTRO, name_of_bird)
                    create_if_directory_not_exists(path_to_bird_spectro)
                    path_to_bird = "%s/%s"%(_PATH_TO_SOUNDS, name_of_bird)
                    create_if_directory_not_exists(path_to_bird)
                    print("_download_and_convert_to_spectro:", path_to_bird)
                    return_value = fetcher.download_birdsound_if_not_exists(birdsound=data, path=path_to_bird)
                    if return_value == 0:
                        path_to_wav = "%s/%s.wav"%(path_to_bird, data.file_name)
                        name_of_bird_spectro = "%s/%s"%(path_to_bird_spectro,data.file_name)
                        spectrogramer.perform_save_multiple_spectrograms(224, 224, path_to_wav, name_of_bird_spectro, ".png", _THRESHOLD)
                        print("Removing %s ..." % (path_to_wav))
                        remove(path_to_wav)
                        print("Removing %s has been successful." % (path_to_wav))
            for dir_name in listdir(_PATH_TO_SOUNDS):
                print("Removing %s/%s ..." % (_PATH_TO_SOUNDS, dir_name))
                rmdir("%s/%s"%(_PATH_TO_SOUNDS, dir_name))
                print("Removing %s/%s has been successful." % (_PATH_TO_SOUNDS, dir_name))
    else:
        print("%s: %s already exists."%(_PATH_OF_THIS_FILE, path_to_tfrecords))

def create_spectro_for_records(recordings):
    fetcher = FetchData()
    spectrogramer = WavPreprocessor()
    list_of_records = fetcher.get_list_of_birdsounds(metadata=recordings)
    for data in list_of_records:
        name_of_bird = "%s_%s" % (data.generic_name, data.species_name)
        path_to_bird_spectro = "%s/%s" % (_PATH_TO_SPECTRO, name_of_bird)
        create_if_directory_not_exists(path_to_bird_spectro)
        path_to_bird = "%s/%s" % (_PATH_TO_SOUNDS, name_of_bird)
        create_if_directory_not_exists(path_to_bird)
        print("_download_and_convert_to_spectro:", path_to_bird)
        return_value = fetcher.download_birdsound_if_not_exists(birdsound=data, path=path_to_bird)
        if return_value == 0:
            path_to_wav = "%s/%s.wav" % (path_to_bird, data.file_name)
            name_of_bird_spectro = "%s/%s" % (path_to_bird_spectro, data.file_name)
            spectrogramer.perform_save_multiple_spectrograms(224, 224, path_to_wav, name_of_bird_spectro, ".png",
                                                             _THRESHOLD)
            print("Removing %s ..." % (path_to_wav))
            remove(path_to_wav)
            print("Removing %s has been successful." % (path_to_wav))

def _convert_spectrograms_to_tfrecords(destination_directory, train, validation):
    create_if_directory_not_exists(destination_directory)
    run(destination_directory, _PATH_TO_SPECTRO, train, validation)

    


