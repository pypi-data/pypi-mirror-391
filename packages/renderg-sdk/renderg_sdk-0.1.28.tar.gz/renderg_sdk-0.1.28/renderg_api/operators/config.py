
class ConfigOperator(object):

    def __init__(self, connect):
        self._connect = connect

    def get_cluster_list(self):
        response = self._connect.get(self._connect.urls.GetClusterList)
        return response

    def get_zone_list(self, cluster_id=""):
        params = {}
        if cluster_id:
            params = {
                'cluster_id': cluster_id
            }
        response = self._connect.get(self._connect.urls.GetZoneList, params)
        return response