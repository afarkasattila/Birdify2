from preprocessing.sounds.download_birdify_data import BirdSoundHandler, BirdSound
from optparse import OptionParser

def setup_options():
    parser = OptionParser()
    parser.add_option("-p","--path", action="store", type="string", dest="path_to_wav", help='Where to save the wav file.')
    parser.add_option("-i","--sound_id", action="store", type="int", dest="sound_id", help='The id of the sound (from xeno-canto). Default = 383766')
    options, _ = parser.parse_args()
    return options

if __name__ == "__main__":
    parser = setup_options()
    if parser.path_to_wav is None:
        path = "./sound_wav"
    else:
        path = parser.path_to_wav
    if parser.sound_id is None:
        name = "383766"
    else:
        name = str(parser.sound_id)

    birdsound = BirdSound(file_name=name, download_url="http://www.xeno-canto.org/%s/download"%(name))
    handler = BirdSoundHandler(bird_sound=birdsound, path=path)
    handler.process_download_single_wav()
    