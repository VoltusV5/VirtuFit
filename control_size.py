from aiogram.types import Message
from aiogram.fsm.context import FSMContext





async def control(message: Message, state: FSMContext):
     data = await state.get_data()
     if data.get('gender') != None and data.get('gender') == 'male':
        if data.get('height') == None:
            return 90<int(message.text)<210
        if data.get('height') <= 150:
            if data.get('chest') == None:
                return 56<int(message.text)<90
            if data.get('waist') == None:
                return 50<int(message.text)<70
            if data.get('hips') == None:
                return 50<int(message.text)<70
            if data.get('shoulder_width') != None:
                return 10<int(message.text)<40
            if data.get('neck') == None:
                return 20<int(message.text)<35
            if data.get('massa') == None:
                return 12<int(message.text)<50
            if data.get('len_arm') == None:
                return 20<int(message.text)<50
        elif data.get('height') <= 175:
            if data.get('chest') == None:
                return 90<int(message.text)<110
            if data.get('waist') == None:
                return 70<int(message.text)<80
            if data.get('hips') == None:
                return 80<int(message.text)<100
            if data.get('shoulder_width') != None:
                return 40<int(message.text)<50
            if data.get('neck') == None:
                return 35<int(message.text)<43
            if data.get('massa') == None:
                return 50<int(message.text)<150
            if data.get('len_arm') == None:
                return 50<int(message.text)<61
        else:
            if data.get('chest') == None:
                return 88<int(message.text)<130
            if data.get('waist') == None:
                return 80<int(message.text)<100
            if data.get('hips') == None:
                return 45<int(message.text)<75
            if data.get('shoulder_width') == None:
                return 35<int(message.text)<60
            if data.get('neck') == None:
                return 30<int(message.text)<55
            if data.get('massa') == None:
                return 50<int(message.text)<200
            if data.get('len_arm') == None:
                return 50<int(message.text)<75   
     else:
         if data.get('gender') != None:
            if data.get('height') == None:
                return 90<int(message.text)<185
            if data.get('height') <= 150:
                if data.get('chest') == None:
                    return 56<int(message.text)<90
                if data.get('waist') == None:
                    return 50<int(message.text)<70
                if data.get('hips') == None:
                    return 50<int(message.text)<70
                if data.get('shoulder_width') != None:
                    return 10<int(message.text)<40
                if data.get('chest_girl') != None:
                    return 40<int(message.text)<70
                if data.get('neck') == None:
                    return 20<int(message.text)<35
                if data.get('massa') == None:
                    return 12<int(message.text)<50
                if data.get('len_arm') == None:
                    return 20<int(message.text)<50
            elif data.get('height') <= 165:
                if data.get('chest') == None:
                    return 80<int(message.text)<115
                if data.get('waist') == None:
                    return 60<int(message.text)<85
                if data.get('hips') == None:
                    return 80<int(message.text)<120
                if data.get('shoulder_width') != None:
                    return 25<int(message.text)<40
                if data.get('chest_girl') != None:
                    return 70<int(message.text)<105
                if data.get('neck') == None:
                    return 25<int(message.text)<42
                if data.get('massa') == None:
                    return 40<int(message.text)<150
                if data.get('len_arm') == None:
                    return 30<int(message.text)<75
            else:
                if data.get('chest') == None:
                    return 85<int(message.text)<130
                if data.get('waist') == None:
                    return 60<int(message.text)<95
                if data.get('hips') == None:
                    return 90<int(message.text)<135
                if data.get('shoulder_width') == None:
                    return 25<int(message.text)<40
                if data.get('chest_girl') == None:
                    return 70<int(message.text)<105
                if data.get('neck') == None:
                    return 27<int(message.text)<42
                if data.get('massa') == None:
                    return 50<int(message.text)<200
                if data.get('len_arm') == None:
                    return 35<int(message.text)<75  