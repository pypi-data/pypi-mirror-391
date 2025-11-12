import renderg_utils


class ParamChecker:

    def __init__(self, api, analyze_obj):
        self.api = api
        self.analyze_obj = analyze_obj

        self.info_path = self.analyze_obj.info_path
        self.warning_path = self.analyze_obj.warning_path

        self.info_data = renderg_utils.read_json(self.info_path)
        self.render_layers = {}

    @property
    def layers(self):
        return self.info_data.get('scene_info', {}).get('render_params', {}).get('layers', {})

    @property
    def layer_names(self):
        return list(set(layer['layer_name'] for layer in self.layers))

    @property
    def scene_path(self):
        return self.analyze_obj.dcc_file

    @property
    def analyze_version(self):
        return self.info_data.get("analysis_version", "")

    def set_render_layers(self, layers):
        if not layers:
            raise ValueError("No render layers specified")

        if not any(layer in self.layer_names for layer in layers.keys()):
            raise ValueError("None of the specified layers exist in the analyzed data")

        res_layers = list()
        for layer_info in self.layers:
            layer_name = layer_info['layer_name']

            res_item = {
                "layer_name": layer_info['layer_name'],
                "enable": False,
                "frame_range": layer_info.get('frame_range', ''),
                "output": layer_info.get('output', '')
            }

            if layer_name in layers:
                res_item.update({
                    "frame_range": layers[layer_name],
                    "enable": True
                })
            res_layers.append(res_item)
        self.render_layers = res_layers


    def execute(self, **kwargs):
        if not self.render_layers:
            raise ValueError("No render layers set. Please call set_render_layers() first.")

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
            "layers": self.render_layers,
            "farm_envs": env_info,
            "use_custom_params": 1,
        }
        self.info_data["CustomParams"] = CustomParams
        renderg_utils.write_json(self.info_path, self.info_data)




