import cyclone
from twisted.internet import reactor
from twisted.python import log
from twisted.web.static import File
import sockjs.cyclone
import requests
import json
import time
import numpy as np
import unicodedata


class IndexHandler(cyclone.web.RequestHandler):
    """ Serve the chat html page """
    def get(self):

        self.render('./templates/index.html')

class ChatConnection(sockjs.cyclone.SockJSConnection):
    """ Chat sockjs connection """

    def messageReceived(self, message):

        def returnTag(i):
            return tags[i]

        url = 'http://api.pollstr.io/api/classify/classify/'
        bots_responses = {'saludo': 'Hola de nuevo! Como te puedo ayudar?', 'datos': 'Ok, hemos registrado tu problema con datos. Me puedes proporcionar tu numero en el siguiente formato (55-5555-5555) para realizar las consultas correspondientes?'}

        text_encoded = unicodedata.normalize('NFKD', unicode(message)).encode('ASCII', 'ignore')

        text = [text_encoded]

        data = {'data': {'username': 'julio', 'language': 'spanish',
                     'name_classifier': 'temm'}, 'text': text}
        data = json.dumps(data)
        r = requests.post(url=url, data=data)
        category = json.loads(r.text)
        probabilities = category['data']['0']['scores'].values()
        tags = category['data']['0']['scores'].keys()
        probabilities_sorted = list(np.argsort(probabilities))
        tags_sorted = map(returnTag, probabilities_sorted)

        top_category = tags_sorted[-1]
        if (top_category == 'datos'):
            response = bots_responses[top_category]
            self.sendMessage(response)

        elif '55-5555-5555' in text[0]:
            response = 'Ok, parece que tenemos una incidencia masiva. Disculpa las molestias! Puedo ayudarte en algo mas?'
            self.sendMessage(response)

        elif '55-6666-6666' in text[0]:
            response = 'Ok, el problema es que no tienes credito para navegar. Por que no visitas este sitio para hacer una <a href="https://recargamobile.movistar.com.mx/TelefonicaMXMobileWebUI/">recargas</a>.'
            self.sendMessage(response)

        elif 'no' in text[0].lower():
            response = 'Ok, gracias por comunicarte con nosotros. Hasta pronto!'
            self.sendMessage(response)
            self.close()

        else:
            response = 'No capto bien. Me puedes proporcionar tu numero en el siguiente formato (55-5555-5555)?'
            self.sendMessage(response)

ChatRouter = sockjs.cyclone.SockJSRouter(ChatConnection, '/chat')

app = cyclone.web.Application( [ (r"/", IndexHandler) ] +
                                       ChatRouter.urls )

reactor.listenTCP(8000, app)

reactor.run()
