import maya.api.OpenMaya as om
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

from GetMayaInfo import MayaInfo
import codecs
import socket
import array
import json
import sys
import os


class Submit(object):
    def __init__(self, host="127.0.0.1", port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def __enter__(self):
        try:
            self.sock.connect((self.host, self.port))
            return self
        except socket.error as error:
            sys.stderr.write("\n" + str(error) + "\n")
            sys.exit(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.shutdown(socket.SHUT_WR)
        self.sock.close()

    def __send(self, data):
        info = json.dumps(data, encoding="utf-8")
        self.sock.sendall(info)

    def __handle_response(self):
        bf = array.array("u", " " * 4096)
        self.sock.recv_into(bf, 4096)
        try:
            data = bf.tostring()
            return json.loads(data)

        except Exception as error:
            print error

    def get_result(self, data):
        self.__send(data)
        return self.__handle_response()

    def request_job_id(self):
        data = {
            "action": "request_running_script",
            "scenefile": cmds.file(q=True, sn=True),
            "scene_type": 'maya',
            "scene_loaded": 1,
        }
        return self.get_result(data)

    def analysis_over(self):
        data = {
            "action": "finish",
        }
        return self.get_result(data)

    def quit(self):
        data = {
            'action': "exit",
        }
        return self.get_result(data)


connect_to_client = Submit


def main():
    with connect_to_client(port=7457) as context:
        result = context.request_job_id()
        running_script = result.get("running_script", None)
        if not running_script:
            return
        obj = MayaInfo()
        data = obj.get_info()
        work_dir = os.path.dirname(running_script)

        with codecs.open(os.path.join(work_dir, "info.cfg"), "w", encoding="utf-8") as fp:
            fp.write(json.dumps(data, ensure_ascii=False, indent=4))

        with open(os.path.join(work_dir, "over.txt"), "w") as fp:
            fp.write("over")


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


# command
class RenderG_submit(om.MPxCommand):
    kPluginCmdName = "RenderG_submit"

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return RenderG_submit()

    def doIt(self, args):
        main()


def submit(*args, **kwargs):
    mel.eval("RenderG_submit")


# Initialize the plug-in
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.registerCommand(
            RenderG_submit.kPluginCmdName, RenderG_submit.cmdCreator
        )
        customMenu = pm.menu('RenderG', parent="MayaWindow")
        pm.menuItem(label="RenderG_submit", command=submit, parent=customMenu)
    except:
        sys.stderr.write(
            "Failed to register command: %s\n" % RenderG_submit.kPluginCmdName
        )
        raise


# Uninitialize the plug-in
def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(RenderG_submit.kPluginCmdName)
        cmds.deleteUI("MayaWindow|RenderG")
    except:
        sys.stderr.write(
            "Failed to unregister command: %s\n" % RenderG_submit.kPluginCmdName
        )
        raise