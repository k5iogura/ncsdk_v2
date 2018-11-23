# Copyright(c) 2018 Kenji.Ogura
# License: Such as Unauthorized use is prohibited.
# mailto : kenji.ogura@jcom.zaq.ne.jp

import sys
from mvnc import mvncapi as mvnc
import numpy

class detector:
    # graph_filename is graph binary file made by mvNCCompile
    # callback_func is called with image and result
    deviceEmpy = [ 1 for i in range(0, 10) ]
    deviceInfo = True
    output = None
    frames = 0
    def __init__(self, num_elem=10, callback_func=None, graph_filename="graph", used_limit=10):
        self.deviceNo  = -1
        self.initiated = False
        self.callback  = callback_func
        self.device    = None
        self.preproc   = None
        self.postproc  = None

        if detector.deviceInfo:
            mvnc.global_set_option(
                mvnc.GlobalOption.RW_LOG_LEVEL,
                mvnc.LogLevel.DEBUG
            )
            detector.deviceInfo = False

        self.devices = mvnc.enumerate_devices()
        detector.num_device = min(len(self.devices), abs(used_limit))

        for d_idx in range(0, detector.num_device):
            if detector.deviceEmpy[d_idx] == 1:
                detector.deviceEmpy[d_idx] = 0
                self.deviceNo = d_idx
                sys.stdout.write("Using device %d "%(self.deviceNo))
                break
        if self.deviceNo < 0: return

        mvnc.global_set_option(
            mvnc.GlobalOption.RW_LOG_LEVEL,
            mvnc.LogLevel.FATAL
        )

        try:
            self.device = mvnc.Device(self.devices[self.deviceNo])

            self.device.open()

            with open(graph_filename, mode='rb') as f:
                self.graph_data = f.read()

            self.graph_obj = mvnc.Graph('graph'+str(self.deviceNo))

            self.fifo_in, self.fifo_out = self.graph_obj.allocate_with_fifos(
                self.device,
                self.graph_data,
                input_fifo_num_elem=num_elem,
                output_fifo_num_elem=num_elem
            )
            print("RO_CAPACITY",self.fifo_in.get_option(mvnc.FifoOption.RO_CAPACITY))
        except Exception as e:
            print("Exception occurred ",e.args)
            quit()

    def set_preproc(self, preproc_func):
        self.preproc = preproc_func

    def set_postproc(self, postproc_func):
        self.postproc = postproc_func

    def set_callback(self, callback_func):
        self.callback = callback_func

    # kick NCS
    def initiate(self, image_source):
        if self.deviceNo < 0: return

        detector.frames += 1
        self.initiated = True

        resized_image = image_source
        if self.preproc is not None:
            resized_image = self.preproc(image_source)

        self.graph_obj.queue_inference_with_fifo_elem(
            self.fifo_in,
            self.fifo_out,
            resized_image.astype(numpy.float32),
            None
        )

    # get result of NCS and call callback function with image and result
    def finish2(self, image_source=None):
        copy_image = None
        if self.initiated:
            output, _ = self.fifo_out.read_elem()
            if image_source is not None:
                copy_image = image_source.copy()
                self.callback(copy_image, output)
            detector.output = output
            self.initiated = False
        elif image_source is not None:
            copy_image = image_source.copy()
            self.callback(copy_image, detector.output)

        # copy_image may be None, prevent accident in your postproc
        if self.postproc is not None:
            sleff.postproc(copy_image)

        return copy_image

    def finish(self, image_source=None):
        output = self.fetch()
        image = self.apply_callback(image_source, output)
        return self.apply_postproc(image)

    # fetch result NCS
    def fetch(self):
        if self.initiated:
            output, user_obj= self.fifo_out.read_elem()
            detector.output = output
            self.initiated  = False
        return detector.output

    def apply_callback(self, image_source, output):
        copy_image = None
        if image_source is not None and output is not None and self.callback is not None:
            copy_image = image_source.copy()
            self.callback(copy_image, output)
        return copy_image

    def apply_postproc(self, image_source):
        # copy_image may be None, prevent accident in your postproc
        if self.postproc is not None and image_source is not None:
            sleff.postproc(image_source)
        return image_source

    # Clean up the graph and the device
    def close(self):
        if self.deviceNo < 0: return
        self.fifo_in.destroy()
        self.fifo_out.destroy()
        self.graph_obj.destroy()
        self.device.close()
        self.device.destroy()

    def thermal(self):
        if self.deviceNo < 0: return 0.0
        THERMAL_STATS = mvnc.DeviceOption.RO_THERMAL_STATS
        return float(self.device.get_option(THERMAL_STATS)[0])

