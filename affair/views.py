from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
import json
from django.utils import timezone
from affair.models import AffairImg, AffairInfo
from login.models import AccountInfo
from login.views import cookiesVerify


def createAffair(request):
    typeDic = {'study':'学习帮助',
               'life':'日常帮助',
               'restThing':'闲置物品',
               'techNeed':'技术帮助',
               'groupNeed':'组队需求',
               'other':'其他'}

    tagDic = {'errand':'跑腿',
              'takeOut':'外卖',
              'express':'快递',
              'tutor':'辅导',
              'findGroup':'组队',
              'competition':'竞赛',
              'findTheOtherPart':'找伴',
              'findFriend':'找伴'}

    num = []
    temp = 1
    for i in range(10):
        num.append(temp)
        temp=temp*2

    context = {'typeDic':typeDic,'num':num,'tag':tagDic}
    return render(request, 'affair/createAffair.html', context)


def processSubmit(request):
    if request.method == 'POST':
        result = cookiesVerify(request)
        print(request.POST)
        data = request.POST

        if (result == '0'):  # 密码认证正确
            accountInfo = AccountInfo.objects.get(phoneNumber=request.COOKIES['phoneNumber'])
            print(accountInfo.phoneNumber)

            affairInfo = AffairInfo(affairProviderId=accountInfo,
                                    type=data['type'],
                                    affairName=data['affairName'],
                                    affairDetail=data['affairDetail'],
                                    affairCreateTime=timezone.now(),
                                    NeedReceiverNum=int(data['receiverNum'][0])
                                    )

            if(data['reward']==''):
                affairInfo.rewardType = '0'
                affairInfo.rewardMoney = 0
            else:
                judge = '0'   #0代表全是数字，则判断酬劳为RMB
                for c in data['reward']:
                    if((c<='0' or c>='9') and c!='.'):
                        judge = '1'
                        break
                affairInfo.rewardType = '0'
                if(judge == '0'):
                    affairInfo.rewardMoney = float(data['reward'])
                    print(float(data['reward']))
                else:
                    affairInfo.rewardThing = data['reward']


            print(data.getlist('tag'))
            temp = ''
            # reward待补充
            for tag in data.getlist('tag'):  # 里边会有多个标签
                temp = temp + tag + ';'
                print(temp)
            affairInfo.tag = temp
            affairInfo.save()

            count = 0
            for imgFile in request.FILES.getlist('img_file'):
                count = count + 1
                new_img = affairInfo.affairimg_set.create(
                    img=imgFile,
                    name=imgFile.name
                )
            sendBack = {'statusCode': '0'}
            return JsonResponse(sendBack)

        if (result == '1' or result == '2'):
            sendBack = {'statusCode': result}
            return JsonResponse(sendBack)
        sendBack = {'statusCode': '3'}
        return JsonResponse(sendBack)

    print('图片来了？？？')
    return JsonResponse(sendBack)
