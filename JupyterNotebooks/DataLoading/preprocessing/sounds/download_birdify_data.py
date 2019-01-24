from json import dump, loads, load
from numpy import int16
from os import makedirs, remove
from os.path import exists, isfile
from pydub import AudioSegment
from scipy.io import wavfile
from urllib.error import URLError
from urllib.request import urlopen, urlretrieve

ROOT_SOUND_PATH = ".././soundsamples/"
ROOT_DATA_PATH = ".././metadata/"
METADATA_FILE = "metadata.txt"
ERRORS_FILE = ".././download_errors.txt"
LIST_OF_AREAS = ["africa", "america", "asia", "australia", "europe"]

def create_directory_structure():
    """
    Creates a directory hierarchy for birdsounds and metadata.
    The hierarchy should look like this:
        /soundsamples
            /africa
            /america
            ...
            /europe
        /metadata
            /africa
                metadata.txt
            /america
                metadata.txt
            ...
            /europe
                metadata.txt
        download_errors.txt
    """
    if not exists(ROOT_SOUND_PATH):
        makedirs(ROOT_SOUND_PATH)
        for area in LIST_OF_AREAS:
            makedirs("%s%s" % (ROOT_SOUND_PATH, area))
    if not exists(ROOT_DATA_PATH):
        makedirs(ROOT_DATA_PATH)
        for area in LIST_OF_AREAS:
            makedirs("%s%s" % (ROOT_DATA_PATH, area))
        for area in LIST_OF_AREAS:
            with open("%s%s/%s" % (ROOT_DATA_PATH, area, METADATA_FILE), mode='w', encoding='utf-8') as f:
                dump([], f)
    if not exists(ERRORS_FILE):
        with open(ERRORS_FILE, mode='w', encoding='utf-8') as f:
            dump([], f)

def create_if_directory_not_exists(dir):
    if not exists(dir):
        print("Creating directory %s..." % (dir))
        makedirs(dir)
        print("Directory %s created." % (dir))

def check_file_already_exists(file_name, country, area):
    group = file_name[:2]
    return isfile("%s%s/%s/%s/%s.wav" % (ROOT_SOUND_PATH, area, country, group, file_name))


class BirdSound:
    """
    Simple bean to store the useful metadata of a birdsound.
    """
    def __init__(self, file_name, generic_name=None, species_name=None, subspecies_name=None,
                english_name=None, country=None, location=None, latitude=None, longitude=None, download_url=None, area=None):
        if area is not None:
            self.area = area
        self.file_name = file_name
        self.generic_name = generic_name
        self.species_name = species_name
        self.subspecies_name = subspecies_name
        self.english_name = english_name
        self.generic_name = generic_name
        self.country = country
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.download_url = download_url

class BirdSoundHandler:
    """
    The BirdSoundHandler class is responsible for downloading the corresponding audio file
    and convert it suitably.
    """

    sample_rate = 44100

    def __init__(self, bird_sound, path=None):
        self.group = bird_sound.file_name[:2]
        #self.area = bird_sound.area
        self.country = bird_sound.country
        self.file_name = bird_sound.file_name
        self.url = bird_sound.download_url
        if path is None:
            self.path = "%s%s/%s/%s/" % (ROOT_SOUND_PATH, bird_sound.area, bird_sound.country, self.group)
        else:
            self.path = "%s/"%(path)

    def download_mp3(self):
        create_if_directory_not_exists(self.path)
        path_mp3 = "%s%s.mp3" % (self.path, self.file_name)
        try:
            print("Downloading file from %s" % (self.url))
            urlretrieve(self.url, path_mp3)
        except URLError as e:
            print("Download from %s failed." % (self.url))
            return None
        print("Download from %s completed." % (self.url))
        print("File saved to %s" % (path_mp3))
        return path_mp3

    def convert_mp3_to_wav(self, path_mp3):
        try:
            sound = AudioSegment.from_mp3(path_mp3)
            path_wav = "%s%s.wav" % (self.path, self.file_name)
            print("Converting %s to %s ..." % (path_mp3, path_wav))
            sound.export(path_wav, format="wav")
        except Exception:
            print("Decoding %s failed because of corrupted file." % (path_mp3))
            print("Please, remove the file %s. File location can be found in %s." % (path_mp3, ERRORS_FILE))
            error = {path_mp3 : self.file_name}
            with open(ERRORS_FILE) as f:
                data = load(f)
            data.extend(error)
            with open(ERRORS_FILE, 'w') as f:
                dump(data, f)
            return None
        return path_wav

    def change_wav(self, path_wav):
        rate, data = wavfile.read(path_wav)
        new_data = data.astype(int16)
        wavfile.write(path_wav, self.sample_rate, new_data)
        return True

    def remove_sound(self, path):
        print("Removing %s ..." % (path))
        remove(path)
        print("Removing %s has been successful." % (path))
        return True

    def process_download_single_wav(self):
        path_mp3 = self.download_mp3()
        _ = self.convert_mp3_to_wav(path_mp3=path_mp3)
        self.remove_sound(path_mp3)

    def process(self):
        print("process: Downloading file from %s" % (self.url))
        path_mp3 = self.download_mp3()
        if path_mp3 is not None:
            path_wav = self.convert_mp3_to_wav(path_mp3)
            if path_wav is not None:
                self.change_wav(path_wav)
                self.remove_sound(path_mp3)
                return 0
            else:
                return -1

class FetchData:
    """
    The FetchData class downloads all audio file and its corresponding metadata
    that bellongs to the specified area.
    """

    query_url = "http://www.xeno-canto.org/api/2/recordings?query="
    pg = "&page="

    def __init__(self, area=None):
        if area in LIST_OF_AREAS:
            self.area = area
        else:
            self.area = LIST_OF_AREAS[-1]

    def get_nr_of_pages(self, url=None):
        if url is None:
            url = "%sarea:%s%s%s" % ( self.query_url, self.area, self.pg, 1)
        try:
            response = urlopen(url)
            html = response.read().decode("utf-8")
            data = loads(html)
            nr_of_pages = data["numPages"]
            return nr_of_pages
        except URLError as e:
            print("Could not send %s request while getting the number of pages." % (url))
            return -1

    def get_records_by_area(self, pg_nr, url=None):
        if url is None:
            url = "%sarea:%s%s%s" % ( self.query_url, self.area, self.pg, str(pg_nr))
        try:
            response = urlopen(url)
            html = response.read().decode("utf-8")
            data = loads(html)
            return data["recordings"]
        except URLError as e:
            print("Could not send %s request while getting the records from area %s." % (url, self.area))
            return []

    def check_file_already_exists(self, file_name, country):
        group = file_name[:2]
        return isfile("%s%s/%s/%s/%s.wav" % (ROOT_SOUND_PATH, self.area, country, group, file_name))

    def append_metadata_to_file(self, metadata):
        with open("%s%s/%s" % (ROOT_DATA_PATH, self.area, METADATA_FILE)) as f:
            data = load(f)
        data.extend(metadata)
        with open("%s%s/%s" % (ROOT_DATA_PATH, self.area, METADATA_FILE), "w") as f:
            dump(data, f)

    def get_list_of_birdsounds(self, metadata):
        list_of_records = []
        for record in metadata:
            print("id = ", record["id"], "url = ", record["file"])
            filtered_data = BirdSound(record["id"], record["gen"], record["sp"], record["ssp"], record["en"],
                                    record["cnt"], record["loc"], record["lat"], record["lng"], "https:" + record["file"], self.area)
            list_of_records.append(filtered_data)
        return list_of_records

    def download_birdsound_if_not_exists(self, birdsound, path=None):
        print("download_birdsound_if_not_exists: ",birdsound.download_url, " " ,path)

        if path is None:
            if not self.check_file_already_exists(birdsound.file_name, birdsound.country):
                handler = BirdSoundHandler(birdsound)
                return handler.process()
            else:
                print("The recording with id %s already exists in local storage." % (birdsound.file_name))
        else:
            if not isfile("%s/%s.wav" % (path, birdsound.file_name)):
                handler = BirdSoundHandler(birdsound, path=path)
                return handler.process()
            else:
                print("The recording with id %s already exists in local storage." % (birdsound.file_name))
                return 0

    def process_of_download_birdsound_by_species(self, species):
        create_if_directory_not_exists("../sounds_by_species")
        nr_of_pages = self.get_nr_of_pages() +1
        for i in range(1, nr_of_pages):
            print("Page number = %d" % (i))
            records = self.get_records_by_area(i)
            list_of_records = self.get_list_of_birdsounds(records)
            for data in list_of_records:
                sp = "%s %s"%(data.generic_name, data.species_name)
                if sp in species:
                    path = "../sounds_by_species/%s"%(sp)
                    _ = self.download_birdsound_if_not_exists(data, path=path)

    def run(self):
        nr_of_pages = self.get_nr_of_pages() +1
        for i in range(1, nr_of_pages):
            records = self.get_records_by_area(i)
            self.append_metadata_to_file(records)
            list_of_records = self.get_list_of_birdsounds(records)
            for data in list_of_records:
                _ = self.download_birdsound_if_not_exists(data)
