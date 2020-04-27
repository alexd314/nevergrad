# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from math import sqrt, tan, pi
import numpy as np
import nevergrad as ng
import PIL
import PIL.Image
import os
from nevergrad.common.typetools import ArrayLike
from .. import base


class Image(base.ExperimentFunction):
    def __init__(self, problem_type: str = "recovering", index_pb: int = 0) -> None:
        """
        problem_type: the type of problem we are working on.
           recovering: we directly try to recover the target image.
        index_pb: the index of the problem, inside the problem type.
           For example, if problem_type is "recovering" and index_pb == 0,
           we try to recover the face of O. Teytaud.
        """

        # Storing high level information.
        self.domain_shape = (256, 256, 3)
        self.problem_type = problem_type
        self.index_pb = index_pb

        # Storing data necessary for the problem at hand.
        assert problem_type == "recovering"  # For the moment we have only this one.
        assert index_pb == 0  # For the moment only 1 target.
        path = os.path.dirname(__file__) + "/headrgb_olivier.png"
        image = PIL.Image.open(path).resize((self.domain_shape[0], self.domain_shape[1]), PIL.Image.ANTIALIAS)
        self.data = np.asarray(image)[:,:,:3]  # 4th Channel is pointless here, only 255.

        # if problem_type == "adversarial": 
        #     assert index_pb <= 100  # If we have that many target images.
        #     self.data = ..... (here we load the imagee correspnding to index_pb and problem_type; this is
        #         # the attacked image.)

        array = ng.p.Array(shape=self.domain_shape, mutable_sigma=True,)
        array.set_mutation(sigma=35)
        array.set_bounds(lower=0, upper=255, method="clipping", full_range_sampling=True)
        max_size = ng.p.Scalar(lower=1, upper=200).set_integer_casting()
        array.set_recombination(ng.p.mutation.Crossover(axis=(0, 1), max_size=max_size)).set_name("")  # type: ignore
        super().__init__(self._loss, array)
        self.register_initialization()
        self._descriptors.update()

    def _loss(self, x: np.ndarray) -> float:
        x = np.array(x, copy=False).ravel()
        x = x.reshape(self.domain_shape)
        assert x.shape == self.domain_shape, f"Shape = {x.shape} vs {self.domain_shape}"


        # Define the loss, in case of recovering: the goal is to find the target image.
        assert self.problem_type == "recovering"
        assert self.index_pb == 0
        value = np.sum(np.fabs(np.subtract(x, self.data)))

        # Here we should implement "adversarial" and others.
        return value

    # pylint: disable=arguments-differ
    def evaluation_function(self, x: np.ndarray) -> float:  # type: ignore
        loss = self.function(x)
        return loss