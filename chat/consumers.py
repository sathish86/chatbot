import re
import json
import logging
from channels import Group
from channels.sessions import channel_session
from .models import Room, BotQuestions

log = logging.getLogger(__name__)

@channel_session
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        prefix, label = message['path'].decode('ascii').strip('/').split('/')
        if prefix != 'chat':
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return

    log.debug('chat connect room=%s client=%s:%s', 
        room.label, message['client'][0], message['client'][1])
    
    # Need to be explicit about the channel layer so that testability works
    # This may be a FIXME?
    Group('chat-'+label, channel_layer=message.channel_layer).add(message.reply_channel)

    message.channel_session['room'] = room.label

def frame_answer(room, label, message):
    log.debug('frame answer')
    all_user_inputs = room.messages.filter(handle="User")
    if len(all_user_inputs) != 4:
        return "Input messages are not fed into the system correctly"
    else:
        if all_user_inputs[3].message.lower() == "yes":
            smoker_non = "smoker"
        elif all_user_inputs[3].message.lower() == "no":
            smoker_non = "non-smoker" 
        else:
            smoker_non = all_user_inputs[3].message

        text = "{0} was born in {1} and is a {2} {3}.".format(all_user_inputs[0].message, 
                    all_user_inputs[2].message, all_user_inputs[1].message, smoker_non)
        log.debug(text)
        return text


@channel_session
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        log.debug('recieved message, buy room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", text)
        return
    
    if set(data.keys()) == set(('done', )):
        result = frame_answer(room, label, message)
        result_dict = {"message": result}
        Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(result_dict)})
        return

    if set(data.keys()) != set(('message', )):
        log.debug("ws message unexpected format data=%s", data)
        return

    if data:
        log.debug('chat message room=%s message=%s', 
            room.label, data['message'])
        
        current_question = room.messages.last().bot_question.id
        current_question_obj = room.messages.last().bot_question
        data.update({"bot_question": current_question_obj,
                    'handle': 'User',})

        message_data = room.messages.create(**data)
        next_question = int(current_question) + 1 
        try:
            next_question_obj = BotQuestions.objects.get(pk=next_question)
        except BotQuestions.DoesNotExist:
            log.debug('ws question does not exist label=%s', label)
            return

        data_q = {
            'handle': 'Bot',
            'message': next_question_obj.question,
            'bot_question': next_question_obj}
        message_data_q = room.messages.create(**data_q)
        
        # See above for the note about Group
        Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(message_data.as_dict())})
        Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(message_data_q.as_dict())})

@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        Group('chat-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, Room.DoesNotExist):
        pass
