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
    def cameras(self):
        return self.info_data.get("cameras", [])

    @property
    def layers(self):
        return self.info_data.get("layers", {})

    @property
    def plugins(self):
        return self.info_data.get("plugins", [])

    @property
    def project_path(self):
        return self.analyze_obj.project_path

    @property
    def scene_path(self):
        return self.analyze_obj.dcc_file

    @property
    def analyze_version(self):
        return self.info_data.get("analysis_version", "")

    def set_render_layers(self, layers):
        if not layers:
            raise ValueError("No layers specified")

        if not any(layer in self.layers for layer in layers.keys()):
            raise ValueError("None of the specified layers exist in the analyzed data")

        res_layers = dict()
        for layer_name, layer_info in self.layers.items():
            render_frame = "{}x{}".format(layer_info["frame_range"], layer_info.get("byFrame", 1))
            render_width = layer_info["width"]
            render_height = layer_info["height"]
            render_enable = layer_info["renderable"] == 1
            res_layers[layer_name] = {
                "ForceRenderFrames": render_frame,
                "RenderWidth": render_width,
                "RenderCameras": "",
                "RenderHeight": render_height,
                "Renderable": render_enable,
            }
            if layer_name in layers:
                res_layers[layer_name].update(layers[layer_name])

        self.render_layers = res_layers

    def execute(self, **kwargs):
        if not self.render_layers:
            raise ValueError("No render layers specified, please set render layers using set_render_layers() method")

        if "zone_id" not in kwargs:
            raise ValueError('Required "zone_id" not specified')
        if "ram_limit" not in kwargs:
            raise ValueError('Required "ram_limit" not specified')

        self.api.set_hardware_config(self.analyze_obj.job_id, kwargs["zone_id"], kwargs["ram_limit"])

        env_info = self.api.env.get_env_info_by_id(self.analyze_obj.env_id)
        layer_mode = kwargs.get("layer_mode", "") or env_info.get("layer_mode", "")

        all_lights = env_info.get("renderSetup_includeAllLights", False)
        if "renderSetup_includeAllLights" in kwargs:
            all_lights = kwargs["renderSetup_includeAllLights"]

        CustomParams = {
            "ChunkSize": kwargs.get("ChunkSize", 1),
            "Mark": kwargs.get("Mark", ""),
            "layered_rendering": int(kwargs.get("layered_rendering", False)),
            "layer_mode": layer_mode,
            "renderSetup_includeAllLights": all_lights,
            "PriorityFrames": kwargs.get("PriorityFrames", ""),
            "task_timeout": kwargs.get("task_timeout", 0),
            "renderg_layers": self.render_layers,
            "farm_envs": env_info,
		    "use_custom_params": 1,
        }
        self.info_data["CustomParams"] = CustomParams
        renderg_utils.write_json(self.info_path, self.info_data)




