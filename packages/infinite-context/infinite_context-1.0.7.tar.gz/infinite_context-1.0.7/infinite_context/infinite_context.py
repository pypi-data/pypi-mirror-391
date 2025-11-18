# This code is an algorithm projected, architected and developed by Sapiens Technology®️ and aims to enable an infinite context for Artificial Intelligence algorithms focusing on language models.
# To enable infinite context, input and output data are saved in encoded and indexed local files for later consultation.
# When a new prompt is sent, this indexed data is consulted so that only the excerpts referring to the prompt are inserted in the current context,
# thus avoiding memory overflow due to excessive context with unnecessary excerpts.
# To assist in this process, summary techniques are also applied to make the data even more synthesized so that it never exceeds the real limit of the context of the model that is being requested at the time.
class InfiniteContext:
    def __init__(self, display_error_point=True):
        try:
            self.__display_error_point = bool(display_error_point) if type(display_error_point) in (bool, int, float) else True
            def installModule(module_name='', version=None):
                try:
                    from subprocess import check_call, CalledProcessError
                    from sys import executable
                    module_name = str(module_name).strip()
                    module_name = f'{module_name}=={version}' if version else module_name
                    check_call([executable, '-m', 'pip', 'install', module_name])
                    print(f'Module {module_name} installed successfully!')
                except CalledProcessError as error:
                    print(f'ERROR installing the module "{module_name}": {error}')
                    print('Run the command:\npip install '+module_name)
            from traceback import print_exc
            from os import path, environ, walk, remove
            from tempfile import gettempdir, NamedTemporaryFile
            from hashlib import sha256
            from datetime import datetime
            from logging import getLogger, ERROR, WARNING
            from io import BytesIO, StringIO
            from collections import defaultdict
            from urllib.request import urlopen
            from time import sleep
            from re import split, search, sub
            from json import loads
            from zipfile import ZipFile
            from csv import reader, writer
            from statistics import median, stdev, variance
            from random import shuffle
            self.__print_exc = print_exc
            self.__path, self.__environ, self.__walk, self.__remove = path, environ, walk, remove
            self.__gettempdir, self.__NamedTemporaryFile = gettempdir, NamedTemporaryFile
            self.__sha256 = sha256
            self.__datetime = datetime
            self.__getLogger, self.__ERROR, self.__WARNING = getLogger, ERROR, WARNING
            self.__BytesIO, self.__StringIO = BytesIO, StringIO
            self.__defaultdict = defaultdict
            self.__urlopen = urlopen
            self.__sleep = sleep
            self.__split, self.__search, self.__sub = split, search, sub
            self.__loads = loads
            self.__ZipFile = ZipFile
            self.__reader, self.__writer = reader, writer
            self.__median, self.__stdev, self.__variance = median, stdev, variance
            self.__shuffle = shuffle
            try: from perpetual_context import PerpetualContext
            except:
                installModule(module_name='perpetual-context', version='1.1.2')
                from perpetual_context import PerpetualContext
            try: from certifi import where
            except:
                installModule(module_name='certifi', version='2024.2.2')
                from certifi import where
            try: from requests import get, post
            except:
                installModule(module_name='requests', version='2.31.0')
                from requests import get, post
            try: from lxml import html, etree
            except:
                installModule(module_name='lxml', version='5.2.2')
                from lxml import html, etree
            try: from pandas import ExcelFile, read_excel
            except:
                installModule(module_name='pandas', version='2.2.2')
                from pandas import ExcelFile, read_excel
            try: from PIL import Image
            except:
                installModule(module_name='pillow', version='10.3.0')
                from PIL import Image
            try: from numpy import array, argmax
            except:
                installModule(module_name='numpy', version='1.25.2')
                from numpy import array, argmax
            try: from paddleocr import PaddleOCR
            except:
                installModule(module_name='paddlepaddle', version='2.6.0')
                installModule(module_name='paddleocr', version='2.7.3')
                from paddleocr import PaddleOCR
            try: from cv2 import dnn, cvtColor, COLOR_RGB2BGR, imread, VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, imwrite
            except:
                installModule(module_name='opencv-python', version='4.6.0.66')
                from cv2 import dnn, cvtColor, COLOR_RGB2BGR, imread, VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, imwrite
            try:
                from moviepy.editor import VideoFileClip
                import moviepy.config as cfg
            except:
                installModule(module_name='moviepy', version='1.0.3')
                from moviepy.editor import VideoFileClip
                import moviepy.config as cfg
            try: from speech_recognition import Recognizer, AudioFile
            except:
                installModule(module_name='SpeechRecognition', version='3.10.3')
                from speech_recognition import Recognizer, AudioFile
            try: from pydub import AudioSegment
            except:
                installModule(module_name='pydub', version='0.25.1')
                from pydub import AudioSegment
            try: from bs4 import BeautifulSoup
            except:
                installModule(module_name='beautifulsoup4', version='4.12.3')
                from bs4 import BeautifulSoup
            try: from fitz import open as fitz
            except:
                installModule(module_name='PyMuPDF', version='1.24.5')
                from fitz import open as fitz
            try: from docx2txt import process
            except:
                installModule(module_name='docx2txt', version='0.8')
                from docx2txt import process
            self.__perpetual_context = PerpetualContext(display_error_point=self.__display_error_point)
            self.__where = where
            self.__get, self.__post = get, post
            self.__html, self.__etree = html, etree
            self.__ExcelFile, self.__read_excel = ExcelFile, read_excel
            self.__Image = Image
            self.__array, self.__argmax = array, argmax
            self.__PaddleOCR = PaddleOCR
            self.__dnn, self.__cvtColor, self.__COLOR_RGB2BGR, self.__imread, self.__VideoCapture, self.__CAP_PROP_FPS, self.__CAP_PROP_FRAME_COUNT, self.__CAP_PROP_POS_FRAMES, self.__imwrite = dnn, cvtColor, COLOR_RGB2BGR, imread, VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, imwrite
            self.__VideoFileClip, self.__cfg = VideoFileClip, cfg
            self.__Recognizer, self.__AudioFile = Recognizer, AudioFile
            self.__AudioSegment = AudioSegment
            self.__BeautifulSoup = BeautifulSoup
            self.__fitz = fitz
            self.__process = process
            self.__api_url = 'https://api.api-ninjas.com/v1/'
            self.__api_keys = (
                '45IZ33NRKIYq1rXqM0jBIA==ohTy6eXZR59Vg9P4',
                'CTIMzWuijPZEX5ofpEYH4A==eMBiw1ahOn6VV5xJ',
                'Ul2oI2rpJm/qqyj8exteiQ==Ni8X0iX3LqsxOcDn',
                'GOgnb3FonG10lUJUulVrpw==Hos9YqfxfkLmIB67',
                '0Mz7y76NMGq8q11eqRfoGQ==eDKBZX2IbuwwoWON',
                'DtrqS/c+6gHXSGHDNwaQAA==UFlPrOIEFfaP11Dr',
                'rHx0phoFLzPpZ5b+jkTk1g==yK8xRiOazuIAa7bR',
                'xvZitqoinVGEXqJ2CHgcnA==NGL0emAmTZZ3EmPq',
                '0WKYpFdLuhNgOjSTYeMSDw==oGELlNFiP8JNNOOJ',
                'Q+3OT2Zae6V8F0uqbsKo5Q==WpCwNzcviNeOllHc'
            )
            languages1 = ['en', 'pt', 'es', 'fr', 'de', 'it', 'ru', 'ar', 'hi', 'zh-Hant', 'zh-Hans', 'zh', 'af', 'ak', 'sq', 'am', 'hy', 'as', 'ay', 'az', 'bn', 'eu', 'be', 'bho', 'bs']
            languages2 = ['bg', 'my', 'ca', 'ceb', 'co', 'hr', 'cs', 'da', 'dv', 'nl', 'eo', 'et', 'ee', 'fil', 'fi', 'gl', 'lg', 'ka', 'el', 'gn', 'gu', 'ht', 'ha', 'haw', 'iw', 'hmn']
            languages3 = ['hu', 'is', 'ig', 'id', 'ga', 'ja', 'jv', 'kn', 'kk', 'km', 'rw', 'ko', 'kri', 'ku', 'ky', 'lo', 'la', 'lv', 'ln', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml']
            languages4 = ['mt', 'mi', 'mr', 'mn', 'ne', 'nso', 'no', 'ny', 'or', 'om', 'ps', 'fa', 'pl', 'pa', 'qu', 'ro', 'sm', 'sa', 'gd', 'sr', 'sn', 'sd', 'si', 'sk', 'sl']
            languages5 = ['so', 'st', 'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th', 'ti', 'ts', 'tr', 'tk', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'fy', 'xh', 'yi', 'yo', 'zu']
            self.__languages = languages1+languages2+languages3+languages4+languages5
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.__init__: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
    def __getRootDirectory(self):
        try: return str(self.__path.dirname(self.__path.realpath(__file__)).replace('\\', '/')+'/').strip()
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.__getRootDirectory: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return './'
    def __getTemporaryAudioFromVideo(self, video_path=''):
        try:
            exclusion_path = ''
            video_path = str(video_path).strip()
            temporary_file_directory = self.__gettempdir()
            if not temporary_file_directory.endswith('/'): temporary_file_directory += '/'
            audio_name, extension = self.getHashCode(), '.wav'
            state_of_creation = self.saveAudioFromVideo(video_path=video_path, audio_path=temporary_file_directory, audio_name=audio_name, extension=extension)
            if not state_of_creation:
                temporary_file_directory = self.__getRootDirectory()
                state_of_creation = self.saveAudioFromVideo(video_path=video_path, audio_path=temporary_file_directory, audio_name=audio_name, extension=extension)
            exclusion_path = temporary_file_directory+audio_name+extension
            return exclusion_path if state_of_creation else ''
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.__getTemporaryAudioFromVideo: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def __shuffleTuple(self, original_tuple=()):
        try:
            tuple_list = list(original_tuple)
            self.__shuffle(tuple_list)
            return tuple(tuple_list)
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.__shuffleTuple: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return original_tuple
    def existingPath(self, file_path='', show_message=False):
        try:
            result = True
            file_path = str(file_path).strip()
            show_message = bool(show_message) if type(show_message) in (bool, int, float) else False
            if file_path.lower().startswith('http://') or file_path.lower().startswith('https://'):
                try:
                    response = self.__get(file_path)
                    content = str(response.content).replace("b''", '').strip()
                    if response.status_code != 200 or len(content) < 1: result = False
                except: result = False
            elif not self.__path.exists(file_path): result = False
            if not result and show_message: print(f'The path to the "{file_path}" file does not exist.')
            return result
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.existingPath: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return False
    def getHashCode(self):
        try:
            def generateHashCode():
                now = self.__datetime.now()
                formatted_str = now.strftime('%Y%m%d%H%M%S%f')
                try:
                    datetime_bytes = formatted_str.encode()
                    hash_object = self.__sha256(datetime_bytes)
                    hash_code = hash_object.hexdigest()
                except: hash_code = formatted_str
                return hash_code.strip()
            hash_code = generateHashCode()
            return hash_code
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getHashCode: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return 'temp'
    def getFileType(self, file_path=''):
        try:
            file_path = str(file_path).strip()
            file_type = self.__perpetual_context.getFileType(file_path=file_path).strip()
            if len(file_type) < 1 and file_path.lower().startswith('https://') or file_path.lower().startswith('http://'):
                possible_extensions = ('pdf', 'docx', 'txt', 'pptx', 'ppsx', 'pptm', 'xlsx', 'csv', 'webp', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'dng', 'mpo',
                'tif', 'tiff', 'pfm', 'mp3', 'wav', 'mpeg', 'm4a', 'aac', 'ogg', 'flac', 'aiff', 'wma', 'ac3', 'amr', 'mp4', 'avi', 'mkv', 'mov', 'webm', 'flv', '3gp', 'wmv', 'ogv')
                for possible_extension in possible_extensions:
                    if possible_extension in file_path.lower():
                        file_type = possible_extension
                        break
            return file_type
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getFileType: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def countTokens(self, string=''): return self.__perpetual_context.countTokens(string=string)
    def getKeyWords(self, string=''): return self.__perpetual_context.getKeyWords(string=string)
    def getBeginningAndEnd(self, string='', max_tokens=1000, separator=''): return self.__perpetual_context.getBeginningAndEnd(string=string, max_tokens=max_tokens, separator=separator)
    def getBeginningMiddleAndEnd(self, string='', max_tokens=1000, separator=''): return self.__perpetual_context.getBeginningMiddleAndEnd(string=string, max_tokens=max_tokens, separator=separator)
    def getSummaryCode(self, text='', max_tokens=1000): return self.__perpetual_context.getSummaryCode(text=text, max_tokens=max_tokens)
    def getSummaryText(self, text='', max_tokens=1000): return self.__perpetual_context.getSummaryText(text=text, max_tokens=max_tokens)
    def getSummaryTXT(self, file_path='', max_tokens=1000): return self.__perpetual_context.getSummaryTXT(file_path=file_path, max_tokens=max_tokens)
    def imageToBase64(self, file_path=''): return self.__perpetual_context.imageToBase64(file_path=file_path)
    def saveBase64Image(self, base64_string='', file_path='', image_name='', extension=''): return self.__perpetual_context.saveBase64Image(base64_string=base64_string, file_path=file_path, image_name=image_name, extension=extension)
    def saveImageFromPDF(self, pdf_path='', image_path='', image_name='', extension='', page_index=0): return self.__perpetual_context.saveImageFromPDF(pdf_path=pdf_path, image_path=image_path, image_name=image_name, extension=extension, page_index=page_index)
    def getObjectsFromImage(self, file_path='', use_api=True):
        try:
            detected_objects_str = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            use_api = bool(use_api) if type(use_api) in (bool, int, float) else True
            def detectObjectsWithAPI(image_path):
                def getResponse(image_binary, api_key):
                    api_url = self.__api_url+'objectdetection'
                    response, object_names = self.__post(api_url, files={'image': image_binary}, headers={'X-Api-Key': api_key}), []
                    if response.status_code == 200:
                        json_object = response.json()
                        for object_name in json_object:
                            object_name = str(object_name['label']).strip()
                            if object_name not in object_names: object_names.append(object_name)
                    return sorted(object_names)
                api_keys = self.__shuffleTuple(original_tuple=self.__api_keys)
                detected_objects, detected_objects_str = [], ''
                if image_path.startswith('http://') or image_path.startswith('https://'):
                    try:
                        self.__environ['SSL_CERT_FILE'] = self.__where()
                        self.__getLogger('requests').setLevel(self.__ERROR)
                    except: pass
                    image_binary = self.__BytesIO(self.__get(image_path).content)
                else: image_binary = open(image_path, 'rb')
                for api_key in api_keys:
                    detected_objects = getResponse(image_binary, api_key)
                    if len(detected_objects) > 0: break
                detected_objects_str = ', '.join(detected_objects) if len(detected_objects) > 0 else ''
                return detected_objects_str.strip()
            def detectObjectsLocally(image_path):
                def loadModel():
                    net = self.__dnn.readNet('yolov3.weights', 'yolov3.cfg')
                    layer_names = net.getLayerNames()
                    output_layers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]
                    with open('coco.names', 'r') as file: classes = [line.strip() for line in file.readlines()]
                    return net, output_layers, classes
                def loadImage(image_path):
                    if image_path.startswith('http://') or image_path.startswith('https://'):
                        try:
                            self.__environ['SSL_CERT_FILE'] = self.__where()
                            self.__getLogger('requests').setLevel(self.__ERROR)
                        except: pass
                        response = self.__get(image_path)
                        image = self.__Image.open(self.__BytesIO(response.content))
                        image = self.__array(image)
                        image = self.__cvtColor(image, self.__COLOR_RGB2BGR)
                    else: image = self.__imread(image_path)
                    return image
                net, output_layers, classes = loadModel()
                image = loadImage(image_path)
                blob = self.__dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outputs, detected_objects = net.forward(output_layers), []
                for output in outputs:
                    for detection in output:
                        scores = detection[5:]
                        class_id = self.__argmax(scores)
                        confidence = scores[class_id]
                        if confidence > 0.8: detected_objects.append(str(classes[class_id]).strip())
                detected_objects = list(set(detected_objects))
                detected_objects_str = ', '.join(sorted(detected_objects)) if len(detected_objects) > 0 else ''
                return detected_objects_str.strip()
            detected_objects_str = detectObjectsWithAPI(image_path=file_path) if use_api else ''
            if len(detected_objects_str) < 1 or not use_api: detected_objects_str = detectObjectsLocally(image_path=file_path)
            return detected_objects_str
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getObjectsFromImage: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def getTextsFromImage(self, file_path='', use_api=True, language=None):
        try:
            complete_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            use_api = bool(use_api) if type(use_api) in (bool, int, float) else True
            language = language.strip() if type(language) == str else 'en'
            def detectTextsWithAPI(image_path):
                def getResponse(image_binary, api_key):
                    api_url = self.__api_url+'imagetotext'
                    response, tokens = self.__post(api_url, files={'image': image_binary}, headers={'X-Api-Key': api_key}), []
                    if response.status_code == 200:
                        json_object = response.json()
                        for texts in json_object:
                            token = str(texts['text']).strip()
                            tokens.append(token)
                    return tokens
                api_keys = self.__shuffleTuple(original_tuple=self.__api_keys)
                all_tokens, complete_text = [], ''
                if image_path.startswith('http://') or image_path.startswith('https://'):
                    try:
                        self.__environ['SSL_CERT_FILE'] = self.__where()
                        self.__getLogger('requests').setLevel(self.__ERROR)
                    except: pass
                    image_binary = self.__BytesIO(self.__get(image_path).content)
                else: image_binary = open(image_path, 'rb')
                for api_key in api_keys:
                    all_tokens = getResponse(image_binary, api_key)
                    if len(all_tokens) > 0: break
                complete_text = ' '.join(all_tokens) if len(all_tokens) > 0 else ''
                return complete_text.strip()
            def detectTextsLocally(image_path):
                self.__getLogger('ppocr').setLevel(self.__WARNING)
                optical_character_recognition = self.__PaddleOCR(use_angle_cls=True, lang=language)
                if image_path.startswith('http://') or image_path.startswith('https://'):
                    try:
                        self.__environ['SSL_CERT_FILE'] = self.__where()
                        self.__getLogger('requests').setLevel(self.__ERROR)
                    except: pass
                    response = self.__get(image_path)
                    image_path = self.__array(self.__Image.open(self.__BytesIO(response.content)))
                results = optical_character_recognition.ocr(image_path, cls=True)
                try: extracted_text = ' '.join([linha[-1][0] for linha in results[0]])
                except: extracted_text = ''
                return extracted_text
            complete_text = detectTextsWithAPI(image_path=file_path) if use_api else ''
            if len(complete_text) < 1 or not use_api: complete_text = detectTextsLocally(image_path=file_path)
            return complete_text
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getTextsFromImage: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def getColorsFromImage(self, file_path='', maximum_colors=5):
        try:
            highlighted_colors = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            number_of_colors = int(maximum_colors) if type(maximum_colors) in (bool, int, float) else 5
            def getColorName(rgb_tuple):
                basic_colors, minimal_colors = {
                    (0, 0, 0): 'black',
                    (128, 128, 128): 'gray',
                    (255, 255, 255): 'white',
                    (255, 0, 0): 'red',
                    (0, 135, 0): 'green',
                    (0, 0, 255): 'blue',
                    (255, 255, 0): 'yellow',
                    (255, 165, 0): 'orange',
                    (255, 59, 203): 'pink',
                    (128, 0, 128): 'purple',
                    (133, 84, 42): 'brown'
                }, {}
                for key, name in basic_colors.items():
                    red, green, blue = key
                    red_difference = (red-rgb_tuple[0])**2
                    green_difference = (green-rgb_tuple[1])**2
                    blue_difference = (blue-rgb_tuple[2])**2
                    minimal_colors[(red_difference+green_difference+blue_difference)] = name
                return minimal_colors[min(minimal_colors.keys())]
            def getDominantColors(image_path, number_of_colors):
                if image_path.startswith('http://') or image_path.startswith('https://'):
                    try:
                        self.__environ['SSL_CERT_FILE'] = self.__where()
                        self.__getLogger('requests').setLevel(self.__ERROR)
                    except: pass
                    response = self.__get(image_path)
                    image_path = self.__BytesIO(response.content)
                image = self.__Image.open(image_path)
                image = image.resize((100, 100))
                image = image.convert('RGB')
                pixels = list(image.getdata())
                color_counts = self.__defaultdict(int)
                for pixel in pixels: color_counts[pixel] += 1
                grouped_colors = self.__defaultdict(int)
                for color, count in color_counts.items():
                    color_name = getColorName(color)
                    grouped_colors[color_name] += count
                sorted_colors = sorted(grouped_colors.items(), key=lambda x: x[1], reverse=True)
                dominant_colors = sorted_colors[:number_of_colors]
                dominant_colors = ', '.join(sorted([color[0] for color in dominant_colors]))
                return dominant_colors.strip()
            highlighted_colors = getDominantColors(image_path=file_path, number_of_colors=number_of_colors)
            return highlighted_colors
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getColorsFromImage: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def saveImageFromVideo(self, video_path='', image_path='', image_name='', extension='', hour=0, minute=0, second=0):
        try:
            video_path, image_path, image_name, extension = str(video_path).strip(), str(image_path).strip(), str(image_name).strip(), str(extension).strip()
            if not self.existingPath(file_path=video_path, show_message=True): return False
            hour = max((0, int(hour))) if type(hour) in (bool, int, float) else 0
            minute = max((0, int(minute))) if type(minute) in (bool, int, float) else 0
            second = max((0, int(second))) if type(second) in (bool, int, float) else 0
            time_seconds = hour * 3600 + minute * 60 + second
            if video_path.lower().startswith('https://') or video_path.lower().startswith('http://'):
                try:
                    self.__environ['SSL_CERT_FILE'] = self.__where()
                    self.__getLogger('requests').setLevel(self.__ERROR)
                except: pass
            video_capture = self.__VideoCapture(video_path)
            if not video_capture.isOpened(): return False
            fps = video_capture.get(self.__CAP_PROP_FPS)
            frame_count = int(video_capture.get(self.__CAP_PROP_FRAME_COUNT))
            video_duration = frame_count / fps
            if time_seconds > video_duration: time_seconds = video_duration/2
            frame_number = int(time_seconds * fps)
            video_capture.set(self.__CAP_PROP_POS_FRAMES, frame_number)
            result, frame = video_capture.read()
            if len(image_path) < 1: image_path = './'
            elif not image_path.endswith('/'): image_path += '/'
            if len(image_name) < 1: image_name = 'IMAGE'
            if len(extension) < 1: extension = '.png'
            if not extension.startswith('.'): extension = '.'+extension
            output_path = image_path+image_name+extension
            if result: self.__imwrite(output_path, frame)
            else: return False
            video_capture.release()
            return True
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.saveImageFromVideo: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return False
    def saveAudioFromVideo(self, video_path='', audio_path='', audio_name='', extension=''):
        try:
            video_path, audio_path, audio_name, extension = str(video_path).strip(), str(audio_path).strip(), str(audio_name).strip(), str(extension).strip()
            if not self.existingPath(file_path=video_path, show_message=True): return False
            self.__getLogger('matplotlib.font_manager').disabled = True
            self.__getLogger('moviepy').setLevel(self.__ERROR)
            self.__getLogger("moviepy.audio.io.AudioFileClip").setLevel(self.__ERROR)
            self.__environ['IMAGEIO_FFMPEG_LOG_LEVEL'] = 'ERROR'
            self.__cfg.VERBOSITY = 0
            if video_path.lower().startswith('https://') or video_path.lower().startswith('http://'):
                try:
                    self.__environ['SSL_CERT_FILE'] = self.__where()
                    self.__getLogger('requests').setLevel(self.__ERROR)
                except: pass
            video = self.__VideoFileClip(video_path)
            audio = video.audio
            if len(audio_path) < 1: audio_path = './'
            elif not audio_path.endswith('/'): audio_path += '/'
            if len(audio_name) < 1: audio_name = 'AUDIO'
            if len(extension) < 1: extension = '.wav'
            if not extension.startswith('.'): extension = '.'+extension
            output_path = audio_path+audio_name+extension
            if extension.lower().endswith('.mp3'): audio.write_audiofile(output_path, codec='libmp3lame', bitrate='128k', fps=audio.fps, logger=None)
            else: audio.write_audiofile(output_path, codec='pcm_s16le', fps=audio.fps, logger=None)
            video.close()
            return True
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.saveAudioFromVideo: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return False
    def __getAudioTranscript(self, file_path='', language=None):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            language = language.lower().strip() if type(language) == str else ''
            recognizer, audio = self.__Recognizer(), None
            file_type = self.getFileType(file_path=file_path).lower()
            def downloadAudio(url):
                try:
                    self.__environ['SSL_CERT_FILE'] = self.__where()
                    self.__getLogger('requests').setLevel(self.__ERROR)
                except: pass
                temporary_file = self.__NamedTemporaryFile(delete=False, suffix='.'+file_type)
                response = self.__get(url)
                temporary_file.write(response.content)
                temporary_file.close()
                return temporary_file.name
            def audioHasMoreThan59Seconds(file_path):
                try:
                    if file_path.lower().startswith('https://') or file_path.lower().startswith('http://'):
                        try:
                            self.__environ['SSL_CERT_FILE'] = self.__where()
                            self.__getLogger('urllib.request').setLevel(self.__ERROR)
                        except: pass
                        response = self.__urlopen(file_path)
                        audio_data = response.read()
                        audio_stream = self.__BytesIO(audio_data)
                        if file_type == 'mp3': audio = self.__AudioSegment.from_mp3(audio_stream)
                        else: audio = self.__AudioSegment.from_file(audio_stream)
                    else: audio = self.__AudioSegment.from_file(file_path)
                    duration_seconds = len(audio)/1000
                    if duration_seconds > 59: return True
                    else: return False
                except: return False
            def splitAudio(file_path, maximum_duration=59000):
                audio = self.__AudioSegment.from_file(file_path, format=file_type)
                total_duration, split_files = len(audio), []
                number_of_parts = total_duration//maximum_duration+1
                for index in range(number_of_parts):
                    start = index*maximum_duration
                    end = min((index+1)*maximum_duration, total_duration)
                    segment = audio[start:end]
                    with self.__NamedTemporaryFile(delete=False, suffix='.'+file_type) as temporary_file:
                        temporary_file_name = temporary_file.name
                        segment.export(temporary_file_name, format=file_type)
                        split_files.append(temporary_file_name)
                return split_files
            def clearTemporaryFiles(file_paths):
                for file_path in file_paths:
                    try:
                        if self.__path.exists(file_path):
                            self.__remove(file_path)
                    except: pass
            def clearPreviousTemporaryFiles(file_paths=[], file_path=''):
                if len(file_path) > 0:
                    directory_path = self.__path.dirname(file_path)
                    if self.__path.isdir(directory_path):
                        for root, _, files in self.__walk(directory_path):
                            for file in files:
                                _file_path = self.__path.join(root, file)
                                if _file_path != file_path: self.__remove(_file_path)
                if len(file_paths) > 0:
                    directory_path = self.__path.dirname(file_paths[0])
                    if self.__path.isdir(directory_path):
                        for root, _, files in self.__walk(directory_path):
                            for file in files:
                                file_path = self.__path.join(root, file)
                                if file_path not in file_paths: self.__remove(file_path)
            def getTranscript(language='', audio=None): return recognizer.recognize_google(audio, language=str(language).strip())
            if audioHasMoreThan59Seconds(file_path=file_path):
                downloaded = False
                if file_path.lower().startswith('https://') or file_path.lower().startswith('http://'): file_path, downloaded = downloadAudio(url=file_path), True
                split_files, temporary_texts, number_of_errors = splitAudio(file_path=file_path), [], 0
                for temporary_file in split_files:
                    try:
                        if self.__path.exists(temporary_file):
                            if temporary_file.lower().endswith('.mp3') or file_type == 'mp3':
                                audio = self.__AudioSegment.from_mp3(temporary_file)
                                wav_data = self.__BytesIO()
                                audio.export(wav_data, format='wav')
                                wav_data.seek(0)
                                with self.__AudioFile(wav_data) as source: audio = recognizer.record(source)
                            else:
                                with self.__AudioFile(temporary_file) as source: audio = recognizer.record(source)
                        try:
                            if len(language) < 1:
                                try: temporary_result_text = str(getTranscript(language=self.__languages[0], audio=audio)).strip()
                                except: temporary_result_text = ''
                                for _language in self.__languages[1:]:
                                    try:
                                        result_text = str(getTranscript(language=_language, audio=audio)).strip()
                                        if len(result_text) > len(temporary_result_text):
                                            language = _language
                                            break
                                    except: pass
                            else: result_text = str(getTranscript(language=language, audio=audio)).strip()
                        except:
                            self.__sleep(.1)
                            try:
                                if self.__path.exists(temporary_file):
                                    self.__remove(temporary_file)
                            except: pass
                            if number_of_errors > 1:
                                clearPreviousTemporaryFiles(file_paths=split_files, file_path=file_path if downloaded else '')
                                if len(temporary_texts) > 0: result_text = ' '.join(temporary_texts)+' '+result_text
                                return result_text.strip()
                            else: number_of_errors += 1
                        temporary_texts.append(result_text)
                    except: pass
                if len(temporary_texts) > 0: result_text = ' '.join(temporary_texts)
                clearTemporaryFiles(file_paths=split_files)
                if downloaded:
                    try:
                        if self.__path.exists(file_path):
                            self.__remove(file_path)
                    except: pass
            else:
                if file_path.lower().startswith('https://') or file_path.lower().startswith('http://'):
                    try:
                        self.__environ['SSL_CERT_FILE'] = self.__where()
                        self.__getLogger('requests').setLevel(self.__ERROR)
                    except: pass
                    web_data = self.__BytesIO(self.__get(file_path).content)
                    if file_type == 'mp3':
                        web_data.seek(0)
                        audio_segment = self.__AudioSegment.from_mp3(web_data)
                        wav_data = self.__BytesIO()
                        audio_segment.export(wav_data, format='wav')
                        wav_data.seek(0)
                        web_data = wav_data
                    web_data.seek(0)
                    with self.__AudioFile(web_data) as source: audio = recognizer.record(source)
                else:
                    if file_path.lower().endswith('.mp3') or file_type == 'mp3':
                        audio = self.__AudioSegment.from_mp3(file_path)
                        wav_data = self.__BytesIO()
                        audio.export(wav_data, format='wav')
                        wav_data.seek(0)
                        with self.__AudioFile(wav_data) as source: audio = recognizer.record(source)
                    else:
                        with self.__AudioFile(file_path) as source: audio = recognizer.record(source)
                if len(language) < 1:
                    try: temporary_result_text = str(getTranscript(language=self.__languages[0], audio=audio)).strip()
                    except: temporary_result_text = ''
                    for language in self.__languages[1:]:
                        try:
                            result_text = str(getTranscript(language=language, audio=audio)).strip()
                            if len(result_text) > len(temporary_result_text): break
                        except: pass
                else: result_text = str(getTranscript(language=language, audio=audio)).strip()
            return result_text.strip()
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.__getAudioTranscript: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def getAudioTranscript(self, file_path='', language=None):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            language = language.lower().strip() if type(language) == str else ''
            file_type = self.getFileType(file_path=file_path).lower()
            video_formats, exclusion_path = ('mp4', 'avi', 'mkv', 'mov', 'webm', 'flv', '3gp', 'wmv', 'ogv'), ''
            if file_type in video_formats:
                exclusion_path = self.__getTemporaryAudioFromVideo(video_path=file_path)
                result_text = self.__getAudioTranscript(file_path=exclusion_path, language=language)
                try:
                    if len(exclusion_path) > 0 and self.__path.exists(exclusion_path):
                        self.__remove(exclusion_path)
                except: pass
            else: result_text = self.__getAudioTranscript(file_path=file_path, language=language)
            return result_text
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getAudioTranscript: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def countPDFPages(self, file_path=''): return self.__perpetual_context.countPDFPages(file_path=file_path)
    def getSummaryYouTube(self, file_path='', max_tokens=1000):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            def getVideoInfo(url):
                response = self.__get(url)
                if response.status_code != 200: return '', ''
                title_match = self.__search(r'<title>(.*?) - YouTube</title>', response.text)
                title = title_match.group(1) if title_match else ''
                description_match = self.__search(r'"description":{"simpleText":"(.*?)"}', response.text)
                description = description_match.group(1) if description_match else ''
                if description: description = description.encode().decode('unicode_escape')
                channel_match = self.__search(r'"ownerChannelName":"(.*?)"', response.text)
                channel = channel_match.group(1) if channel_match else ''
                publish_date_match = self.__search(r'"publishDate":"(.*?)"', response.text)
                publish_date = publish_date_match.group(1) if publish_date_match else ''
                return title.strip(), description.strip(), channel.strip(), publish_date.strip()
            def getVideoTranscript(url):
                full_transcript = ''
                response = self.__get(url)
                if response.status_code == 200:
                    soup = self.__BeautifulSoup(response.text, 'html.parser')
                    scripts, transcript_data = soup.find_all('script'), None
                    for script in scripts:
                        if 'ytInitialPlayerResponse' in script.text:
                            match = self.__search(r'ytInitialPlayerResponse\s*=\s*({.*?});', script.text)
                            if match:
                                data = self.__loads(match.group(1))
                                transcript_data = data.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
                                break
                    if transcript_data:
                        transcript_url = transcript_data[0]['baseUrl']
                        transcript_response = self.__get(transcript_url)
                        if transcript_response.status_code == 200:
                            transcript_soup, transcript = self.__BeautifulSoup(transcript_response.text, 'xml'), []
                            for text in transcript_soup.find_all('text'): transcript.append(text.text.strip())
                            if len(transcript) > 0:
                                full_transcript = ' '.join(transcript)
                                full_transcript = '**In the video you can hear the following:** '+full_transcript
                return full_transcript.strip()
            result_text, text_complements = getVideoTranscript(url=file_path), ''
            if len(result_text) < 1: return self.__perpetual_context.getSummaryYouTube(file_path=file_path, max_tokens=max_tokens)
            title, description, channel, publish_date = getVideoInfo(url=file_path)
            if len(channel) > 0: text_complements += f'Name of this YouTube channel: **{channel}**\n\n'
            if len(title) > 0: text_complements += f'## {title}\n\n'
            if len(publish_date) > 0: text_complements += f'Publication date: **{publish_date}**\n\n'
            if len(description) > 0: text_complements += f'{description}\n\n'
            if len(text_complements) > 0: result_text = text_complements+result_text
            number_of_tokens = self.countTokens(string=result_text)
            if number_of_tokens > max_tokens: result_text = self.getBeginningMiddleAndEnd(string=result_text, max_tokens=max_tokens)
            return result_text.strip()
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryYouTube: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryYouTube(file_path=file_path, max_tokens=max_tokens)
    def getSummaryWEBPage(self, file_path='', max_tokens=1000):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            response = self.__get(file_path)
            if response.status_code == 200:
                elements = self.__html.fromstring(response.content).xpath('//h1|//h2|//h3|//h4|//h5|//h6|//p')
                for element in elements:
                    if element.tag.lower().strip().startswith('h1'): hash = '# '
                    elif element.tag.lower().strip().startswith('h2'): hash = '## '
                    elif element.tag.lower().strip().startswith('h3'): hash = '### '
                    elif element.tag.lower().strip().startswith('h4'): hash = '#### '
                    elif element.tag.lower().strip().startswith('h5'): hash = '##### '
                    elif element.tag.lower().strip().startswith('h6'): hash = '###### '
                    else: hash = ''
                    result_text += hash+element.text_content().strip()+'\n'
                result_text = result_text.strip()
                if len(result_text) > 0:
                    result_text = f'## Contents of the WEB address: {file_path}\n\n{result_text}'
                    number_of_tokens = self.countTokens(string=result_text)
                    if number_of_tokens > max_tokens: result_text = self.getSummaryText(text=result_text, max_tokens=max_tokens)
                elif len(result_text) < 1: return self.__perpetual_context.getSummaryWEBPage(file_path=file_path, max_tokens=max_tokens)
                return result_text
            else: return self.__perpetual_context.getSummaryWEBPage(file_path=file_path, max_tokens=max_tokens)
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryWEBPage: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryWEBPage(file_path=file_path, max_tokens=max_tokens)
    def getSummaryPDF(self, file_path='', max_tokens=1000, main_page=None, use_api=True, language=None):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            main_page = max(1, int(main_page)) if type(main_page) in (bool, int, float) else None
            use_api = bool(use_api) if type(use_api) in (bool, int, float) else True
            language = language.strip() if type(language) == str else 'en'
            def extractTextFromPDF(pdf_path):
                if pdf_path.lower().startswith('https://') or pdf_path.lower().startswith('http://'):
                    try:
                        self.__environ['SSL_CERT_FILE'] = self.__where()
                        self.__getLogger('requests').setLevel(self.__ERROR)
                    except: pass
                    response = self.__get(pdf_path)
                    pdf_bytes = self.__BytesIO(response.content)
                    document = self.__fitz(stream=pdf_bytes, filetype='pdf')
                else: document = self.__fitz(pdf_path)
                number_of_pages, text, tokens_per_page = len(document), '', max_tokens
                if main_page != None: tokens_per_page = max(1, (max_tokens/(number_of_pages-1)))
                def readAsImage(page_index):
                    temporary_file_directory = self.__gettempdir()
                    if not temporary_file_directory.endswith('/'): temporary_file_directory += '/'
                    image_name, extension, text = self.getHashCode(), '.png', ''
                    delete_file = self.saveImageFromPDF(pdf_path=file_path, image_path=temporary_file_directory, image_name=image_name, extension=extension, page_index=page_index)
                    if delete_file:
                        exclusion_path = temporary_file_directory+image_name+extension
                        text += self.getTextsFromImage(file_path=exclusion_path, use_api=use_api, language=language)+'\n\n'
                        try:
                            if len(exclusion_path) > 0 and self.__path.exists(exclusion_path):
                                self.__remove(exclusion_path)
                                print(page_index)
                        except: pass
                    return text
                for page_index in range(number_of_pages):
                    try: page_text = document.load_page(page_index).get_text().strip()+'\n\n'
                    except: page_text = readAsImage(page_index=page_index)
                    if len(page_text.strip()) < 1: page_text = readAsImage(page_index=page_index)
                    number_of_tokens = self.countTokens(string=page_text) if main_page not in (None, page_index+1) else 0
                    if number_of_tokens > tokens_per_page: page_text = self.getBeginningMiddleAndEnd(string=page_text, max_tokens=tokens_per_page)
                    text += page_text
                document.close()
                text = f'**This PDF document has a total of {number_of_pages} pages**\n\n{text}'
                return text
            result_text = extractTextFromPDF(pdf_path=file_path).strip()
            if len(result_text) < 1: return self.__perpetual_context.getSummaryPDF(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
            else:
                number_of_tokens = self.countTokens(string=result_text)
                if number_of_tokens > max_tokens: result_text = self.getBeginningMiddleAndEnd(string=result_text, max_tokens=max_tokens)
                return result_text
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryPDF: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryPDF(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
    def getSummaryWord(self, file_path='', max_tokens=1000, main_page=None, characters_per_page=4000):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            main_page = max(1, int(main_page)) if type(main_page) in (bool, int, float) else None
            characters_per_page = max((1, int(characters_per_page))) if type(characters_per_page) in (bool, int, float) else 4000
            docx_data = None
            if file_path.lower().startswith('https://') or file_path.lower().startswith('http://'):
                try:
                    self.__environ['SSL_CERT_FILE'] = self.__where()
                    self.__getLogger('requests').setLevel(self.__ERROR)
                except: pass
                docx_data = self.__BytesIO(self.__get(file_path).content)
            complete_text = self.__process(docx_data if docx_data != None else file_path)
            paragraphs = self.__split('\n+', complete_text)
            current_page, pages = '', []
            tokens_per_paragraph = max_tokens if type(main_page) != type(None) else max_tokens/max((1, len(paragraphs)))
            for paragraph in paragraphs:
                current_page, paragraph = current_page.strip(), paragraph.strip()
                if main_page == None:
                    number_of_tokens = self.countTokens(string=paragraph)
                    if number_of_tokens > tokens_per_paragraph: paragraph = self.getSummaryText(text=paragraph, max_tokens=tokens_per_paragraph)
                if len(current_page) + len(paragraph) > characters_per_page:
                    if len(current_page) > 0: pages.append(current_page)
                    current_page = paragraph + '\n'
                else: current_page += paragraph + '\n'
            if len(current_page) > 0: pages.append(current_page.strip())
            if len(pages) > 0:
                if type(main_page) != type(None):
                    number_of_pages = len(pages)
                    possible_pages = (max((1, main_page-1)), main_page, min((main_page+1, number_of_pages)))
                    tokens_per_page = max_tokens/max((1, max((number_of_pages, number_of_pages-3))))
                    new_page, new_pages = '', []
                    for index, page in enumerate(pages):
                        page_number, new_page = index+1, page.strip()
                        if page_number not in possible_pages:
                            number_of_tokens = self.countTokens(string=new_page)
                            if number_of_tokens > tokens_per_page: new_page = self.getBeginningMiddleAndEnd(string=new_page, max_tokens=tokens_per_page)
                        if page_number == possible_pages[0]: new_page = f'\nPAGE {main_page}:\n{new_page}'
                        if page_number == possible_pages[2]: new_page += '\n'
                        new_pages.append(new_page)
                    pages = new_pages.copy()
                result_text = '**Microsoft Word File**\n\n'+'\n'.join(pages)
                number_of_tokens = self.countTokens(string=result_text)
                if number_of_tokens > max_tokens: result_text = self.getBeginningMiddleAndEnd(string=result_text, max_tokens=max_tokens)
            else: result_text = self.__perpetual_context.getSummaryWord(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
            return result_text.strip()
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryWord: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryWord(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
    def getSummaryPowerPoint(self, file_path='', max_tokens=1000, main_page=None):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            main_page = max(1, int(main_page)) if type(main_page) in (bool, int, float) else None
            def extractTextFromXML(xml_content):
                root, text_parts = self.__etree.XML(xml_content), []
                for element in root.iter():
                    if element.tag.endswith('}p'):
                        paragraph = ''.join(element.itertext()).strip()
                        if paragraph:
                            if element.getparent().tag.endswith('}title'): text_parts.append(paragraph+'\n')
                            else: text_parts.append(paragraph)
                return self.__sub(r'<[^>]*>', '', '\n'.join(text_parts))
            def getSlideNumber(file_name):
                match = self.__search(r'slide(\d+)\.xml$', file_name)
                return int(match.group(1)) if match else float('inf')
            bytes_io = None
            if file_path.lower().startswith('https://') or file_path.lower().startswith('http://'):
                try:
                    self.__environ['SSL_CERT_FILE'] = self.__where()
                    self.__getLogger('requests').setLevel(self.__ERROR)
                except: pass
                bytes_io = self.__BytesIO(self.__get(file_path).content)
            with self.__ZipFile(bytes_io if bytes_io != None else file_path, 'r') as pptx:
                slides = [file_info for file_info in pptx.infolist() if file_info.filename.startswith('ppt/slides/slide') and file_info.filename.endswith('.xml')]
                slides.sort(key=lambda x: getSlideNumber(x.filename))
                number_of_slides = len(slides)
                tokens_per_slide = max_tokens/max((1, number_of_slides-1)) if type(main_page) != type(None) else max_tokens
                for slide_number, slide_info in enumerate(slides):
                    with pptx.open(slide_info.filename) as slide_file:
                        slide_number, slide_text = slide_number+1, extractTextFromXML(slide_file.read()).strip()
                        if type(main_page) != type(None) and slide_number != main_page:
                                number_of_tokens = self.countTokens(string=slide_text)
                                if number_of_tokens > tokens_per_slide: slide_text = self.getSummaryText(text=slide_text, max_tokens=tokens_per_slide)
                        result_text += f'SLIDE {slide_number}\n{slide_text}\n\n'
            if len(result_text) > 0: result_text = '**Microsoft PowerPoint File**\n\n'+result_text.strip()
            else: return self.__perpetual_context.getSummaryPowerPoint(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
            number_of_tokens = self.countTokens(string=result_text)
            if number_of_tokens > max_tokens: result_text = self.getSummaryText(text=result_text, max_tokens=max_tokens)
            return result_text
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryPowerPoint: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryPowerPoint(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
    def __getSummaryCSV(self, file_path='', max_tokens=1000, separator=None, table_name=''):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            table_name = str(table_name).strip()
            csv_data, csv_reader, data = [], [], []
            if file_path.lower().startswith('https://') or file_path.lower().startswith('http://'):
                try:
                    self.__environ['SSL_CERT_FILE'] = self.__where()
                    self.__getLogger('requests').setLevel(self.__ERROR)
                except: pass
                csv_data = self.__get(file_path).text.splitlines()
            len_csv_data = len(csv_data)
            if len_csv_data > 0:
                if type(separator) != type(None): csv_reader = self.__reader(csv_data, delimiter=str(separator))
                else: csv_reader = self.__reader(csv_data)
                data = list(csv_reader)
            else:
                with open(file_path, mode='r', newline='') as csv_file:
                    if type(separator) != type(None): csv_reader = self.__reader(csv_file, delimiter=str(separator))
                    else: csv_reader = self.__reader(csv_file)
                    data = list(csv_reader)
            def removeEmptyRowsAndColumns(matrix):
                if len(table_name) > 0: matrix = [row for row in matrix if any(cell is not None and cell != '' and cell[:9] != 'Unnamed: ' for cell in row)]
                else: matrix = [row for row in matrix if any(cell is not None and cell != '' for cell in row)]
                transposed_matrix = list(map(list, zip(*matrix)))
                if len(table_name) > 0: transposed_matrix = [column for column in transposed_matrix if any(cell is not None and cell != '' and cell[:9] != 'Unnamed: ' for cell in column)]
                else: transposed_matrix = [column for column in transposed_matrix if any(cell is not None and cell != '' for cell in column)]
                cleaned_matrix = list(map(list, zip(*transposed_matrix)))
                return cleaned_matrix
            cleaned_data = removeEmptyRowsAndColumns(matrix=data)
            output = self.__StringIO()
            if type(separator) != type(None): csv_writer = self.__writer(output, delimiter=str(separator))
            else: csv_writer = self.__writer(output)
            for row in cleaned_data: csv_writer.writerow(row)
            result_text = output.getvalue()
            output.close()
            def rowsSummary(string, max_tokens):
                def getRecords(csv_string, number_of_parts):
                    data = self.__StringIO(csv_string)
                    data_reader = self.__reader(data)
                    rows = list(data_reader)
                    data_rows, header = rows[1:], rows[0]
                    middle_start = len(data_rows)//2-2
                    middle_end = middle_start + number_of_parts
                    middle = data_rows[middle_start:middle_end]
                    first, last = data_rows[:number_of_parts], data_rows[-number_of_parts:]
                    output = self.__StringIO()
                    data_writer = self.__writer(output)
                    result = [header]+first+middle+last
                    data_writer.writerows(result)
                    csv_output = output.getvalue()
                    output.close()
                    return csv_output
                index, rows_length = 0, max((0, len(string.splitlines())-1))
                while index < rows_length:
                    string = getRecords(csv_string=string, number_of_parts=max((1, int(rows_length/(index+2)))))
                    number_of_tokens = self.countTokens(string=string)
                    if number_of_tokens <= max_tokens: break
                    index += 1
                return string
            number_of_tokens = self.countTokens(string=result_text)
            if number_of_tokens > max_tokens: result_text = rowsSummary(string=result_text, max_tokens=max_tokens)
            def sortList(cells):
                def keyOrdering(item):
                    if item is None: return (0, '')
                    if isinstance(item, complex): return (4, item.real, item.imag)
                    if isinstance(item, str):
                        try: return (2, float(item))
                        except: return (3, item)
                    if isinstance(item, (int, float)): return (1, item)
                    return (5, str(item))
                return sorted(cells, key=keyOrdering)
            convertToFloat = lambda lst: [float(x) if isinstance(x, (bool, int, float, str)) and (str(x).replace('.', '', 1).isdigit() or str(x).lstrip('-').replace('.', '', 1).isdigit()) else 0 for x in lst]
            def mostFrequentElement(column_data): return max(set(sortList(column_data)), key=column_data.count)
            def leastFrequentElement(column_data): return min(set(sortList(column_data)), key=column_data.count)
            def minimumElement(column_data): return sortList(column_data)[0]
            def maximumElement(column_data): return sortList(column_data)[-1]
            def middleElement(column_data):
                middle_index = max((0, int(round(len(column_data)/2))))
                return sortList(column_data)[middle_index]
            def elementsMedian(column_data):
                column_data = convertToFloat(column_data)
                median_value = self.__median(column_data)
                return middleElement(column_data) if median_value == 0 else median_value
            def elementsAverage(column_data):
                column_data = convertToFloat(column_data)
                average = sum(column_data)/len(column_data)
                return middleElement(column_data) if average == 0 else average
            def elementsStandardDeviation(column_data):
                column_data = convertToFloat(column_data)
                return self.__stdev(column_data)
            def elementsVariance(column_data):
                column_data = convertToFloat(column_data)
                return self.__variance(column_data)
            def elementsType(column_data):
                def getType(value):
                    value = str(value).strip()
                    type_obtained = 'str'
                    if value.count('.') == 1:
                        try:
                            float(value)
                            type_obtained = 'float'
                        except: pass
                    elif value.isdigit():
                        try:
                            int(value)
                            type_obtained = 'int'
                        except: pass
                    elif value.lower() in ('false', 'true'): type_obtained = 'bool'
                    elif ((value.count('-') == 1 and value.count('+') == 0) or (value.count('+') == 1 and value.count('-') == 0)) and value.count('j') == 1:
                        try:
                            float(value.replace('-', '').replace('+', '').replace('j', ''))
                            type_obtained = 'complex'
                        except: pass
                    return type_obtained
                elements_type = [getType(element) for element in column_data]
                return mostFrequentElement(elements_type).replace("<class '", '').replace("'>", '')
            matrix, statistical_text, empty_string, lines_number = list(zip(*cleaned_data[1:])), '', 'Empty string', max((0, len(cleaned_data)-1))
            for column_name, vector in zip(cleaned_data[0], matrix):
                statistical_text += f'### {column_name}\n'
                statistical_text += f'**Column type:** {elementsType(vector)}\n'
                least = leastFrequentElement(vector)
                if len(str(least).strip()) < 1: least = empty_string
                most = mostFrequentElement(vector)
                if len(str(most).strip()) < 1: most = empty_string
                if least == most: least = most = 'None are repeated'
                minimum = minimumElement(vector)
                if len(str(minimum).strip()) < 1: minimum = empty_string
                maximum = maximumElement(vector)
                if len(str(maximum).strip()) < 1: maximum = empty_string
                median = elementsMedian(vector)
                if len(str(median).strip()) < 1: median = empty_string
                average = elementsAverage(vector)
                if len(str(average).strip()) < 1: average = empty_string
                standard_deviation = elementsStandardDeviation(vector)
                variance = elementsVariance(vector)
                statistical_text += f'**Least repeated value:** {least}\n'
                statistical_text += f'**Most repeated value:** {most}\n'
                statistical_text += f'**Minimum value:** {minimum}\n'
                statistical_text += f'**Maximum value:** {maximum}\n'
                statistical_text += f'**Median of values:** {median}\n'
                statistical_text += f'**Average of values:** {average}\n'
                statistical_text += f'**Standard deviation of values:** {standard_deviation}\n'
                statistical_text += f'**Variance of values:** {variance}\n'
            statistical_text = statistical_text.strip()
            str_number_of_records, column_metrics = 'Total number of registration lines:', '## COLUMNS METRICS\n'
            result_text = '### Main records contained in the table\n'+result_text
            result_text = f'"{table_name}" tab\n{str_number_of_records} {lines_number}\n\n{result_text}\n' if len(table_name) > 0 else f'# CSV File\n{str_number_of_records} {lines_number}\n\n{result_text}\n'
            result_text += f'{column_metrics}'+statistical_text if len(table_name) > 0 else column_metrics+statistical_text
            number_of_tokens = self.countTokens(string=result_text)
            if number_of_tokens > max_tokens:
                structure = result_text.split('\n\n')
                result_text = structure[0]+'\n\n'+structure[-1]
                number_of_tokens = self.countTokens(string=result_text)
                if number_of_tokens > max_tokens: result_text = self.getBeginningMiddleAndEnd(string=result_text, max_tokens=max_tokens)
            return result_text.strip()
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.__getSummaryCSV: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return ''
    def getSummaryCSV(self, file_path='', max_tokens=1000, separator=None):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            result_text = self.__getSummaryCSV(file_path=file_path, max_tokens=max_tokens, separator=separator)
            if len(result_text) < 1: return self.__perpetual_context.getSummaryCSV(file_path=file_path, max_tokens=max_tokens)
            else: return result_text
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryCSV: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryCSV(file_path=file_path, max_tokens=max_tokens)
    def getSummaryExcel(self, file_path='', max_tokens=1000):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            def excelToCSV(xlsx_path):
                xls, csv_files, sheet_names = self.__ExcelFile(xlsx_path), [], []
                for sheet_name in xls.sheet_names:
                    data_frame = self.__read_excel(xlsx_path, sheet_name=sheet_name)
                    with self.__NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
                        csv_file_name = temp_file.name
                        csv_files.append(csv_file_name), sheet_names.append(sheet_name)
                        data_frame.to_csv(csv_file_name, index=False)
                return csv_files, sheet_names
            bytes_io = None
            if file_path.lower().startswith('https://') or file_path.lower().startswith('http://'):
                try:
                    self.__environ['SSL_CERT_FILE'] = self.__where()
                    self.__getLogger('requests').setLevel(self.__ERROR)
                except: pass
                bytes_io = self.__BytesIO(self.__get(file_path).content)
            csv_files, sheet_names = excelToCSV(xlsx_path=bytes_io if bytes_io != None else file_path)
            tokens_per_table = int(max_tokens/max((1, len(csv_files))))
            for index, csv_file in enumerate(csv_files):
                result_text += self.__getSummaryCSV(file_path=csv_file, max_tokens=tokens_per_table, table_name=sheet_names[index])+'\n\n'
                try:
                    if self.__path.exists(csv_file): self.__remove(csv_file)
                except: pass
            result_text = '# Microsoft Excel File\n'+result_text.strip()
            number_of_tokens = self.countTokens(string=result_text)
            if number_of_tokens > max_tokens: result_text = self.getBeginningMiddleAndEnd(string=result_text, max_tokens=max_tokens)
            if len(result_text) < 1: return self.__perpetual_context.getSummaryExcel(file_path=file_path, max_tokens=max_tokens)
            else: return result_text
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryExcel: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryExcel(file_path=file_path, max_tokens=max_tokens)
    def getSummaryImage(self, file_path='', max_tokens=1000, use_api=True, language=None, maximum_colors=3):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            use_api = bool(use_api) if type(use_api) in (bool, int, float) else True
            language = language.strip() if type(language) == str else 'en'
            maximum_colors = max((1, int(maximum_colors))) if type(maximum_colors) in (bool, int, float) else 3
            list_of_descriptions, file_type = [], self.getFileType(file_path=file_path).upper()
            objects_from_image = self.getObjectsFromImage(file_path=file_path, use_api=use_api).strip()
            texts_from_image = self.getTextsFromImage(file_path=file_path, use_api=use_api, language=language).strip()
            colors_from_image = self.getColorsFromImage(file_path=file_path, maximum_colors=maximum_colors).strip()
            len_objects_from_image, len_texts_from_image, len_colors_from_image = len(objects_from_image), len(texts_from_image), len(colors_from_image)
            if sum((len_objects_from_image, len_texts_from_image, len_colors_from_image)) > 0:
                list_of_descriptions, result_text = [], file_type+' Image content: '
                if len_objects_from_image > 1: list_of_descriptions.append('objects = '+objects_from_image)
                if len_texts_from_image > 0:
                    number_of_tokens = self.countTokens(string=texts_from_image)
                    if number_of_tokens > max_tokens: texts_from_image = self.getBeginningMiddleAndEnd(string=texts_from_image, max_tokens=max_tokens)
                    list_of_descriptions.append('texts = '+texts_from_image)            
                if len_colors_from_image > 1: list_of_descriptions.append('colors = '+colors_from_image)
                result_text += ' - '.join(list_of_descriptions)
                number_of_tokens = self.countTokens(string=result_text)
                if number_of_tokens > max_tokens: result_text = self.getBeginningMiddleAndEnd(string=result_text, max_tokens=max_tokens)
            else: result_text = self.__perpetual_context.getSummaryImage(file_path=file_path, max_tokens=max_tokens)
            return result_text.strip()
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryImage: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryImage(file_path=file_path, max_tokens=max_tokens)
    def getSummaryAudio(self, file_path='', max_tokens=1000, language=None):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            language = language.lower().strip() if type(language) == str else ''
            file_type = self.getFileType(file_path=file_path).upper()
            result_text = self.getAudioTranscript(file_path=file_path, language=language)
            number_of_tokens = self.countTokens(string=result_text)
            if number_of_tokens > max_tokens: result_text = self.getBeginningMiddleAndEnd(string=result_text, max_tokens=max_tokens, separator=' ')
            if len(result_text) > 0: result_text = f'In the {file_type} audio you hear: {result_text}'
            else: result_text = self.__perpetual_context.getSummaryAudio(file_path=file_path, max_tokens=max_tokens)
            number_of_tokens = self.countTokens(string=result_text)
            if number_of_tokens > max_tokens: result_text = self.getBeginningMiddleAndEnd(string=result_text, max_tokens=max_tokens)
            return result_text.strip()
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryAudio: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryAudio(file_path=file_path, max_tokens=max_tokens)
    def getSummaryVideo(self, file_path='', max_tokens=1000, use_api=True, language=None, maximum_colors=3):
        try:
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            use_api = bool(use_api) if type(use_api) in (bool, int, float) else True
            language = language.strip() if type(language) == str else 'en'
            maximum_colors = max((1, int(maximum_colors))) if type(maximum_colors) in (bool, int, float) else 3
            def getVideoDuration(video_path):
                clip = self.__VideoFileClip(video_path)
                duration = clip.duration
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                return f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}'
            def halfTime(time):
                hours, minutes, seconds = map(int, time.split(':'))
                total_seconds = hours*3600+minutes*60+seconds
                half_seconds = total_seconds//2
                half_hours = half_seconds//3600
                half_seconds %= 3600
                half_minutes = half_seconds//60
                half_seconds %= 60
                return f'{half_hours:02}:{half_minutes:02}:{half_seconds:02}'
            def addTimes(time1, time2):
                hours1, minutes1, seconds1 = map(int, time1.split(':'))
                hours2, minutes2, seconds2 = map(int, time2.split(':'))
                seconds1 = hours1*3600+minutes1*60+seconds1
                seconds2 = hours2*3600+minutes2*60+seconds2
                total_seconds = seconds1+seconds2
                hours = total_seconds//3600
                minutes = (total_seconds%3600)//60
                seconds = total_seconds%3600%60
                return f'{hours:02}:{minutes:02}:{seconds:02}'
            middle = halfTime(time=getVideoDuration(video_path=file_path))
            beginning = halfTime(time=middle)
            end = addTimes(time1=middle, time2=beginning)
            times, video_description, delete_file, exclusion_path = (beginning, middle, end), 'In the video you see:\n\n', False, ''
            for time in times:
                try:
                    hour, minute, second = time.split(':')
                    temporary_file_directory = self.__gettempdir()
                    if not temporary_file_directory.endswith('/'): temporary_file_directory += '/'
                    image_name, extension = self.getHashCode(), '.png'
                    delete_file = self.saveImageFromVideo(video_path=file_path, image_path=temporary_file_directory, image_name=image_name, extension=extension, hour=hour, minute=minute, second=second)
                    exclusion_path = temporary_file_directory+image_name+extension
                    objects_from_image = self.getObjectsFromImage(file_path=exclusion_path, use_api=use_api).strip()
                    texts_from_image = self.getTextsFromImage(file_path=exclusion_path, use_api=use_api, language=language).strip()
                    colors_from_image = self.getColorsFromImage(file_path=exclusion_path, maximum_colors=maximum_colors).strip()
                    len_objects_from_image, len_texts_from_image, len_colors_from_image = len(objects_from_image), len(texts_from_image), len(colors_from_image)
                    if len_objects_from_image > 0 and objects_from_image not in video_description: video_description += objects_from_image+'\n'
                    if len_texts_from_image > 0 and texts_from_image not in video_description: video_description += texts_from_image+'\n'
                    if len_colors_from_image > 0 and colors_from_image not in video_description: video_description += 'The predominant colors in the video are '+colors_from_image+'\n'
                    if sum((len_objects_from_image, len_texts_from_image, len_colors_from_image)) < 1: video_description += self.getSummaryImage(file_path=exclusion_path, max_tokens=max_tokens).strip()
                finally:
                    if delete_file:
                        try:
                            if len(exclusion_path) > 0 and self.__path.exists(exclusion_path):
                                self.__remove(exclusion_path)
                        except: pass
                if len(video_description) > 0: video_description = video_description.strip()+'\n'
            exclusion_path = self.__getTemporaryAudioFromVideo(video_path=file_path)
            audio_transcription = self.getAudioTranscript(file_path=exclusion_path, language=language)
            if delete_file:
                try:
                    if len(exclusion_path) > 0 and self.__path.exists(exclusion_path):
                        self.__remove(exclusion_path)
                except: pass
            if len(audio_transcription) > 0:
                number_of_tokens = self.countTokens(string=audio_transcription)
                if number_of_tokens > max_tokens: audio_transcription = self.getBeginningMiddleAndEnd(string=audio_transcription, max_tokens=max_tokens, separator=' ')
                video_description += '\nIn the video you hear: '+audio_transcription
            number_of_tokens = self.countTokens(string=video_description)
            if number_of_tokens > max_tokens: video_description = self.getSummaryText(text=video_description, max_tokens=max_tokens)
            return video_description.strip()
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryVideo: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryVideo(file_path=file_path, max_tokens=max_tokens)
    def getSummaryFile(self, file_path='', max_tokens=1000, main_page=None, characters_per_page=4000, separator=None, use_api=True, language=None, maximum_colors=3):
        try:
            result_text = ''
            file_path = str(file_path).strip()
            if not self.existingPath(file_path=file_path, show_message=True): return ''
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 1000
            main_page = max(1, int(main_page)) if type(main_page) in (bool, int, float) else None
            characters_per_page = max((1, int(characters_per_page))) if type(characters_per_page) in (bool, int, float) else 4000
            use_api = bool(use_api) if type(use_api) in (bool, int, float) else True
            language = language.strip() if type(language) == str else 'en'
            maximum_colors = max((1, int(maximum_colors))) if type(maximum_colors) in (bool, int, float) else 3
            file_type = self.getFileType(file_path=file_path).lower()
            if len(file_type) < 1: file_type = 'null'
            file_path_lower = file_path.lower()
            pdf_types, word_types, text_types = 'pdf', 'docx', 'txt'
            powerpoint_types = ('pptx', 'ppsx', 'pptm')
            excel_types, csv_types = 'xlsx', 'csv'
            image_types = ('webp', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'dng', 'mpo', 'tif', 'tiff', 'pfm')
            audio_types = ('mp3', 'wav', 'mpeg', 'm4a', 'aac', 'ogg', 'flac', 'aiff', 'wma', 'ac3', 'amr')
            video_types = ('mp4', 'avi', 'mkv', 'mov', 'webm', 'flv', '3gp', 'wmv', 'ogv')
            if file_type == pdf_types: file_text = self.getSummaryPDF(file_path=file_path, max_tokens=max_tokens, main_page=main_page, use_api=use_api, language=language)
            elif file_type == word_types: file_text = self.getSummaryWord(file_path=file_path, max_tokens=max_tokens, main_page=main_page, characters_per_page=characters_per_page)
            elif file_type in powerpoint_types: file_text = self.getSummaryPowerPoint(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
            elif file_type == excel_types: file_text = self.getSummaryExcel(file_path=file_path, max_tokens=max_tokens)
            elif file_type == csv_types: file_text = self.getSummaryCSV(file_path=file_path, max_tokens=max_tokens, separator=separator)
            elif file_type in image_types: file_text = self.getSummaryImage(file_path=file_path, max_tokens=max_tokens, use_api=use_api, language=language, maximum_colors=maximum_colors)
            elif file_type in audio_types: file_text = self.getSummaryAudio(file_path=file_path, max_tokens=max_tokens, language=language)
            elif file_type in video_types: file_text = self.getSummaryVideo(file_path=file_path, max_tokens=max_tokens, use_api=use_api, language=language, maximum_colors=maximum_colors)
            elif file_path_lower.startswith('https://') or file_path_lower.startswith('http://') or file_path_lower.startswith('www.'):
                has_pdf_type = self.__search(r'\b('+pdf_types+r')\b', file_path_lower)
                has_word_type = self.__search(r'\b('+word_types+r')\b', file_path_lower)
                has_powerpoint_type = self.__search(r'\b('+'|'.join(powerpoint_types)+r')\b', file_path_lower)
                has_excel_type = self.__search(r'\b('+excel_types+r')\b', file_path_lower)
                has_csv_type = self.__search(r'\b('+csv_types+r')\b', file_path_lower)
                has_image_type = self.__search(r'\b('+'|'.join(image_types)+r')\b', file_path_lower)
                has_audio_type = self.__search(r'\b('+'|'.join(audio_types)+r')\b', file_path_lower)
                has_video_type = self.__search(r'\b('+'|'.join(video_types)+r')\b', file_path_lower)
                has_text_type = self.__search(r'\b('+text_types+r')\b', file_path_lower)
                if file_type in 'xhtml php aspx': file_text = self.getSummaryWEBPage(file_path=file_path, max_tokens=max_tokens)
                elif 'youtube.com' in file_path_lower or 'youtu.be' in file_path_lower: file_text = self.getSummaryYouTube(file_path=file_path, max_tokens=max_tokens)
                elif 'image' in file_path_lower or '/img/' in file_path_lower or '/image/' in file_path_lower or has_image_type: file_text = self.getSummaryImage(file_path=file_path, max_tokens=max_tokens, use_api=use_api, language=language, maximum_colors=maximum_colors)
                elif has_pdf_type: file_text = self.getSummaryPDF(file_path=file_path, max_tokens=max_tokens, main_page=main_page, use_api=use_api, language=language)
                elif has_word_type: file_text = self.getSummaryWord(file_path=file_path, max_tokens=max_tokens, main_page=main_page, characters_per_page=characters_per_page)
                elif has_powerpoint_type: file_text = self.getSummaryPowerPoint(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
                elif has_excel_type: file_text = self.getSummaryExcel(file_path=file_path, max_tokens=max_tokens)
                elif has_csv_type: file_text = self.getSummaryCSV(file_path=file_path, max_tokens=max_tokens, separator=separator)
                elif has_audio_type: file_text = self.getSummaryAudio(file_path=file_path, max_tokens=max_tokens, language=language)
                elif has_video_type: file_text = self.getSummaryVideo(file_path=file_path, max_tokens=max_tokens, use_api=use_api, language=language, maximum_colors=maximum_colors)
                elif has_text_type: file_text = self.getSummaryTXT(file_path=file_path, max_tokens=max_tokens)
                else: file_text = self.getSummaryWEBPage(file_path=file_path, max_tokens=max_tokens)
            else: file_text = self.getSummaryTXT(file_path=file_path, max_tokens=max_tokens)
            tokens_number = self.countTokens(string=file_text)
            if tokens_number > max_tokens: file_text = self.__getBeginningAndEnd(string=file_text, max_tokens=max_tokens)
            result_text = file_text.strip()
            if len(result_text) < 1: return self.__perpetual_context.getSummaryFile(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
            else: return result_text
        except Exception as error:
            error_message = 'ERROR in InfiniteContext.getSummaryFile: '+str(error)
            print(error_message)
            try: self.__print_exc() if self.__display_error_point else None
            except: pass
            return self.__perpetual_context.getSummaryFile(file_path=file_path, max_tokens=max_tokens, main_page=main_page)
    def saveContext(self, user_id=0, dialog_id=0, prompt='', answer=''): return self.__perpetual_context.saveContext(user_id=user_id, dialog_id=dialog_id, prompt=prompt, answer=answer)
    def deleteContext(self, user_id=0, dialog_id=0): return self.__perpetual_context.deleteContext(user_id=user_id, dialog_id=dialog_id)
    def getContext(self, user_id=0, dialog_id=0, config=None): return self.__perpetual_context.getContext(user_id=user_id, dialog_id=dialog_id, config=config)
# This code is an algorithm projected, architected and developed by Sapiens Technology®️ and aims to enable an infinite context for Artificial Intelligence algorithms focusing on language models.
# To enable infinite context, input and output data are saved in encoded and indexed local files for later consultation.
# When a new prompt is sent, this indexed data is consulted so that only the excerpts referring to the prompt are inserted in the current context,
# thus avoiding memory overflow due to excessive context with unnecessary excerpts.
# To assist in this process, summary techniques are also applied to make the data even more synthesized so that it never exceeds the real limit of the context of the model that is being requested at the time.
