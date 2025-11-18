#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 Pietro Rocchio.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr
import numpy as np

class myblock(gr.sync_block):
    def __init__(self, gain = 1.0):
        gr.sync_block.__init__(
            self,
            name = 'My Multiply Block',
            in_sig = [np.float32], # Tipologia dati ingresso
            out_sig = [np.float32] # Tipologia dati uscita
        )
        self.gain = gain

    def work(self, input_items, output_items):
        output_items[0][:] = input_items[0] * self.gain
        return len(output_items[0])