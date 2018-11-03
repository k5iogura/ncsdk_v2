#! /usr/bin/env python3

# Copyright(c) 2018 Kenji.Ogura
# License: MIT See LICENSE file in root directory.


from mvnc import mvncapi as mvnc
import numpy

class detector:
    # graph_filename is graph binary file made by mvNCCompile
    # callback_func is called with image and result
    def __init__(self, callback_func, graph_filename="graph"):
        self.initiated = False
        self.output    = None
        self.callback  = callback_func
        self.preproc   = None
        self.postproc  = None

        mvnc.global_set_option(
            mvnc.GlobalOption.RW_LOG_LEVEL,
            mvnc.LogLevel.DEBUG
        )

        self.devices = mvnc.enumerate_devices()
        if len(self.devices) == 0:
            print('No devices')
            quit()

        mvnc.global_set_option(
            mvnc.GlobalOption.RW_LOG_LEVEL,
            mvnc.LogLevel.FATAL
        )

        try:
            self.device = mvnc.Device(self.devices[0])

            self.device.open()

            with open(graph_filename, mode='rb') as f:
                self.graph_data = f.read()

            self.graph_obj = mvnc.Graph('graph1')

            self.fifo_in, self.fifo_out = self.graph_obj.allocate_with_fifos(
                self.device,
                self.graph_data
            )
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
        self.initiated = True

        if self.preproc is not None:
            resized_image = self.preproc(image_source)

        self.graph_obj.queue_inference_with_fifo_elem(
            self.fifo_in,
            self.fifo_out,
            resized_image.astype(numpy.float32),
            resized_image
        )

    # get result of NCS and call callback function with image and result
    def finish(self, image_source=None):
        copy_image = None
        if self.initiated:
            output, _ = self.fifo_out.read_elem()
            if image_source is not None:
                copy_image = image_source.copy()
                self.callback(copy_image, output)
            self.output = output
            self.initiated = False
        elif image_source is not None:
            copy_image = image_source.copy()
            self.callback(copy_image, self.output)

        # copy_image may be None, prevent accident in your postproc
        if self.postproc is not None:
            sleff.postproc(copy_image)

        return copy_image

    # Clean up the graph and the device
    def close(self):
        self.fifo_in.destroy()
        self.fifo_out.destroy()
        self.graph_obj.destroy()
        self.device.close()
        self.device.destroy()

