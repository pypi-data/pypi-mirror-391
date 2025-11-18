from enum import Enum, unique


@unique
class URL(Enum):
    """
    GET的参数用params，
    POST参数用data，
    """

    """
    :type:表单报告
    """
    pageFormReportDetail = '/formReport/detail/pageFormReportDetail', 'POST'  # 获取表单收集数据
    getFormReportDetail = '/formReport/getFormReportDetail', 'POST'  # 获取表单报告数据(曝光/点击)
    getFormPerformanceTrend = 'formReport/getFormPerformanceTrend', 'POST'

    """
    :type 群组
    """
    editCrowdPackage = '/crowdPackage/editCrowdPackage', 'POST'
    crowdPersonListInPackage = '/crowdPackage/crowdPersonList', 'POST'
    crowdPackageDetail = '/crowdPackage/detail', 'POST'
    crowdPackageList = '/crowdPackage/list', 'POST'

    """
    :type 表单操作
    """
    deleteForm = '/form/deleteFormInfo', 'GET'
    getFormList = '/form/getFormList', 'POST'
    getFormInfo = '/form/getFormInfo', 'GET'

    """
    :type 素材收藏
    """
    saveUniversalContent = "/universalContent/saveUniversalContent", 'POST'
    deleteUniversalContent = "/universalContent/deleteUniversalContent", 'GET'
    updateUniversalContent = "/universalContent/updateUniversalContent", 'POST'
    queryUniversalContent = "/universalContent/query", 'POST'
    updateCampaignUsed = "/universalContent/updateCampaignUsed",'POST'
    queryUsedDetail = "/universalContent/queryUsedDetail", 'POST'

    @property
    def method(self):
        return self.value[1]

    @property
    def url(self):
        return self.value[0]


if __name__ == '__main__':
    print(URL.pageFormReportDetail.method)
    print(URL.getFormReportDetail.url)
