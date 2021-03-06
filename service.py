#!/usr/bin/python

import json
import time

import falcon
import onnx
import torch
import numpy as np
import caffe2.python.onnx.backend as backend
from torchvision import datasets, transforms

PORT_NUMBER = 8080
start = time.time()

# Load the ONNX model
model = onnx.load("model.onnx")

# Check that the IR is well formed
onnx.checker.check_model(model)


rep = backend.prepare(model, device="CUDA:0")  # or "CUDA:0"

transform = transforms.Compose([transforms.ToTensor(),
                                transforms.Normalize((0.5,), (0.5,)),
                                ])

testset = datasets.MNIST('./MNIST_data/', train=False, download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=64, shuffle=False)
images, labels = next(iter(testloader))
images = images.view(images.shape[0], -1)
image_count = images.size()[0]
end = time.time()
print("Loading time: {0:f} secs)".format(end - start))


# API Handler for Iris images
class MNIST(object):
    """Handle classification requests for MNIST dataset by ID"""

    def on_get(self, req, resp, index):
        if index < image_count:
            payload = {}
            payload['label'] = int(labels[index])
            img = images[index].view(1, 784)
            outputs = rep.run(img.numpy())
            predicted = int(np.argmax(outputs))
            payload['predicted'] = predicted
            resp.body = json.dumps(payload)
            resp.status = falcon.HTTP_200
        else:
            raise falcon.HTTPBadRequest(
                "Index Out of Range. ",
                "The requested index must be between 0 and {:d}, inclusive.".format(image_count - 1)
            )


# API Handler for example message
class Intro(object):
    """Example of invoking the endpoint for classifying an image from the MNIST dataset"""

    def on_get(self, req, resp):
        resp.body = '{"message": \
                    "This service verifies a model using the MNIST Test data set. Invoke using the form /mnist/<index ' \
                    'of test image>. For example, /mnist/24"}'
        resp.status = falcon.HTTP_200
