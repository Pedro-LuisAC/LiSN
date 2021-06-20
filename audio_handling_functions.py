import os
import pyaudio
import wave
import sys
import audioop
import math
from pydub import AudioSegment
from pydub.playback import play
from math import log
import global_variables
import sys
import threading
from random import randrange

from time import sleep
 
global_variables.initialize()

#adicionar funcionamento somente com uma placa de som
#calibração - dBFS para dBSPL - adicionar apenas um fator de conversão escondido
#adicionar 4 blocos de excução
#Bloco de resultados com variaveis de inicialização
#Logica de execução de parada baseada em SRT e SE (3 inversoes)
#Gerar relatórios e csv
#3 de 6 palavras repete o nivel
#disable botoes acima de  -- OK
#Corrigir bugs

#Extract information from audio file title - Returns transcripted phrase and number of words of audio files in the path folder by providing an index in the function input. If no index is matched, the function returns False
def get_audio_file_name_by_number(file_number: int):
    path = 'audio_files/'
    files_list = os.listdir(path)
    for file in files_list:
        try:    
            file_number_title = int(file[0:3])            
        except:
            continue
        if file_number == file_number_title:
            file_name = file

            return file_name

    return False

def get_audio_file_name_random(already_used_phrases):
    path = 'audio_files/'
    files_list = os.listdir(path)
    file_name = False
    tries = 0
    while(file_name == False):
        tries += 1
        random_number = randrange(len(files_list))
        aux_file_name = get_audio_file_name_by_number(random_number)
        if aux_file_name not in already_used_phrases:
            file_name = aux_file_name
        elif tries > len(files_list):
            file_name = aux_file_name
    return file_name





def chunk_raw_data(raw_data, chunk_size):
    
    start_index = 0
    end_index = chunk_size - 1
    iterations_number = int(len(raw_data)/(chunk_size) + 1)
    bytes_array = []

    for i in range(iterations_number):
        start_index = end_index + 1
        end_index = end_index + i*chunk_size
        bytes_array.append(raw_data[start_index:end_index])    
    return bytes_array

def get_files_inside_audio_folder(folder):
    path = 'audio_files/' + folder + '/'
    files_list = os.listdir(path)
    return files_list



class AudioWav():
    def __init__(self, file_name):
        path = 'audio_files/'
        self.file_name = file_name
        self.phrase = file_name[7:-4]
        self.words = file_name[4:6]
        self.wf = wave.open(path+file_name, 'rb')
        self.sample_width = self.wf.getsampwidth()
        self.channels = self.wf.getnchannels()
        self.frame_rate = self.wf.getframerate()
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16,
                channels=self.wf.getnchannels(),
                rate=self.wf.getframerate(),
                output=True,
                frames_per_buffer=1024)

        self.audio_segment = AudioSegment.from_wav(path + file_name)
        self.record_seconds = len(self.audio_segment)/1000
        self.chunk = 1024
        self._chunk_position = 0
        self.chunk_list = chunk_raw_data(self.audio_segment.raw_data, self.chunk)
        self.audio_thread = False
        self.kill_thread = False

    def get_dBFS(self):
        return self.audio_segment.dBFS
    
    def apply_gain(self, db_value):
        self.audio_segment = self.audio_segment.apply_gain(db_value)
        self.chunk_list = chunk_raw_data(self.audio_segment.raw_data, self.chunk)
        return
    
    #This function includes the calibration factor
    def set_gain(self, db_value): 
        current_volume = self.audio_segment.dBFS
        correction_value = db_value - current_volume - global_variables.calibration_factor
        self.audio_segment = self.audio_segment.apply_gain(correction_value)
        self.chunk_list = chunk_raw_data(self.audio_segment.raw_data, self.chunk)
        return

    def get_chunk_data(self):
        try:
            data = self.chunk_list[self._chunk_position]  
            self._chunk_position = self._chunk_position + 1
            return data  
        except:
            return False
        return False

    
    def play(self):
        data = self.get_chunk_data()
        while data != False:
            self.stream.write(data)
            data = self.get_chunk_data()
            if self.kill_thread != False:
                return
        self._chunk_position = 0

    def play_loop(self):
        data = self.get_chunk_data()
        while True:
            while data != False:
                self.stream.write(data)
                data = self.get_chunk_data()
                if self.kill_thread != False:
                    return
            self._chunk_position = 0
            data = self.get_chunk_data()


    def play_thread(self):
        self.audio_thread = threading.Thread(target=self.play)
        self.audio_thread.start()
    def play_thread_loop(self):
        self.audio_thread = threading.Thread(target=self.play_loop)
        self.audio_thread.start()

    def stop_thread(self):
        if self.audio_thread != False:
            self.kill_thread = True


    # def max_possible_amplitude(self):
    #     bits = self.sample_width * 8
    #     max_possible_val = (2 ** bits)
    #     # since half is above 0 and half is below the max amplitude is divided
    #     return max_possible_val / 2

    # def rms(self):
    #     return audioop.rms(self.raw_data, self.sample_width)
    


    # def dBFS(self):
    #     rms = self.rms
    #     if not rms:
    #         return -float("infinity")
    #     return ratio_to_db(self.rms / self.max_possible_amplitude)

    # def apply_gain_manually(self, volume_change):
    #     raw_data = audioop.mul(audio_data, self.sample_width, db_to_float(float(volume_change)))
    #     return raw_data
    
    # #implementar controle de volume em tempo real usando variaveis globais. Variaveis globais serao colocadas na main. Colocar um modo de matar o processo e prestar atenção no raw_data
    # def play_pyaudio(self, volume_db):
    #     data = self.wf.readframes(self.chunk)
    #     while len(data) > 0:
    #         current_volume = self.db





#name = get_audio_file_name_by_number("history_1_speaker_1.wav")

# x = AudioWav("history_1_speaker_1.wav")
# print(x.get_dBFS())
# x.set_gain(-10)
# print(x.get_dBFS())

# x.play_thread()
# sleep(2)
# x.set_gain(-35)
# sleep(2)
# x.set_gain(-15)





