import json

from smartpush.base.request_base import RequestBase
from smartpush.base.url_enum import *
from smartpush.email.schema import *


def gen_universal_request_param(universalId, schema, **kwargs):
    """

    :param schema:
    :type universalId:
    kwargs :
    universalName/subUniversal_id/type/flowModal
    """
    universalName = kwargs.get('universalName', gen_universal_name(schema))
    result_schema = get_universal_schema(schema=schema, _id=generate_UUID(8), universalId=universalId,
                                         universalName=universalName)
    requestParam = {
        "universalId": universalId,
        "universalName": universalName,
        "schema": json.dumps(result_schema),
        "subUniversalId": kwargs.get('subUniversal_id', universalId),
        "type": kwargs.get('type', 0),
        "blockType": schema.name,
        "flowModal": kwargs.get('flowModal', '')
    }
    return json.dumps(requestParam)


class UniversalContent(RequestBase):
    # 获取universal创建参数

    # 创建universal
    def create_universal(self, requestParam):
        result = self.request(method=URL.saveUniversalContent.method, path=URL.saveUniversalContent.url,
                              data=requestParam)
        return result

    # 查询universal
    def query_universal(self, universa_name='', blockType_list=None):
        """
        查询素材
        :param blockType_list:
        :param universa_name:
        :return:
        """
        requestParam = {'universa_name': universa_name}
        if blockType_list and type(blockType_list) == list:
            requestParam.update(blockType=blockType_list)
        result = self.request(method=URL.queryUniversalContent.method, path=URL.queryUniversalContent.url,
                              data=requestParam)
        return result

    # 更新universal
    def update_universal(self, universal_list, _type=0):
        """
        更新素材
        :param _type:
        :param universal_list:
                [{"universalId": _dict.get('universa_id'),
                "universalName": _dict.get('universa_name'),
                "schema": json.dumps(result_schema),
                "subUniversalId": _dict.get('subUniversal_id', _dict.get('universa_id')),
                "type": _dict.get('type'),
                "blockType": _dict.get('schema').name,
                "flowModal": ""
                }]
        :return:
        """
        requestParam = {
            "data": universal_list,
            "type": _type
        }
        result = self.request(method=URL.updateUniversalContent.method, path=URL.updateUniversalContent.url,
                              data=requestParam)
        return result

    # 删除universal
    def delete_universal(self, universa_id):
        """
        删除素材
        :param universa_id:
        :return:
        """
        requestParam = {'universalId': universa_id}
        result = self.request(method=URL.deleteUniversalContent.method, path=URL.deleteUniversalContent.url,
                              params=requestParam)
        return result

    def update_campaign_used(self, campaignId, universalIds: list, _type=0):
        """
        更新活动素材关系
        :param campaignId:
        :param universalIds:
        :param _type:
        :return:
        """
        requestParam = {"type": _type, "campaignId": campaignId, "universalIds": universalIds}
        result = self.request(method=URL.updateCampaignUsed.method, path=URL.updateCampaignUsed.url,
                              data=requestParam)
        return result


def generate_UUID(length=None):
    _uuid = str(uuid.uuid4())
    if length:
        return _uuid[:length]
    else:
        return _uuid


def get_time():
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))


def gen_universal_name(schema):
    if schema.value['type']:
        return 'Auto-' + schema.value['type'] + '-' + get_time()
    else:
        return 'Auto-' + generate_UUID(5) + '-' + get_time()


def get_universal_schema(schema, _id, universalId, universalName):
    schema.value.update(id=_id, universalId=universalId, universalName=universalName)
    return schema.value


if __name__ == '__main__':
    print(gen_universal_request_param(generate_UUID(), BlockSchema.Social, ))
