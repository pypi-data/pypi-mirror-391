import renderg_utils


class ParamChecker:

    def __init__(self, api, analyze_obj):
        self.api = api
        self.analyze_obj = analyze_obj

        self.info_path = self.analyze_obj.info_path
        self.warning_path = self.analyze_obj.warning_path

        self.info_data = renderg_utils.read_json(self.info_path)
        self.render_nodes = {}

    @property
    def nodes(self):
        return self.info_data.get("Nodes", {})

    @property
    def scene_path(self):
        return self.analyze_obj.dcc_file

    @property
    def analyze_version(self):
        return self.info_data.get("analysis_version", "")

    def set_render_nodes(self, nodes):
        if not nodes:
            raise ValueError("No render nodes specified")

        if not any(node in self.nodes for node in nodes.keys()):
            raise ValueError("None of the specified nodes exist in the analyzed data")

        res_nodes = dict()
        for node, frames in nodes.items():
            if node not in self.nodes:
                raise ValueError("Render node '{}' does not exist in the analyzed data".format(node))

            res_nodes[node] = {
                "Frames": frames
            }
        self.render_nodes = res_nodes


    def execute(self, **kwargs):
        if not self.render_nodes:
            raise ValueError("No render nodes specified, please set render nodes using 'set_render_nodes' method")

        if "zone_id" not in kwargs:
            raise ValueError('Required "zone_id" not specified')
        if "ram_limit" not in kwargs:
            raise ValueError('Required "ram_limit" not specified')

        self.api.set_hardware_config(self.analyze_obj.job_id, kwargs["zone_id"], kwargs["ram_limit"])

        env_info = self.api.env.get_env_info_by_id(self.analyze_obj.env_id)

        CustomParams = {
            "ChunkSize": kwargs.get("ChunkSize", 1),
            "Mark": kwargs.get("Mark", ""),
            "PriorityFrames": kwargs.get("PriorityFrames", ""),
            "task_timeout": kwargs.get("task_timeout", 0),
            "Nodes": self.render_nodes,
            "farm_envs": env_info,
            "use_custom_params": 1,
        }
        self.info_data["CustomParams"] = CustomParams
        renderg_utils.write_json(self.info_path, self.info_data)




