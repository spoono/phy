# -*- coding: utf-8 -*-

"""Test views."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import numpy as np
from numpy.testing import assert_equal as ae
from pytest import raises

from phy.io.mock import (artificial_waveforms,
                         artificial_spike_clusters,
                         artificial_spike_samples,
                         artificial_masks,
                         artificial_traces,
                         )
from phy.electrode.mea import staggered_positions
from ..views import WaveformView, TraceView, _extract_wave


#------------------------------------------------------------------------------
# Utils
#------------------------------------------------------------------------------

def _show(qtbot, view, stop=False):
    view.show()
    qtbot.waitForWindowShown(view.native)
    if stop:  # pragma: no cover
        qtbot.stop()
    view.close()


#------------------------------------------------------------------------------
# Test utils
#------------------------------------------------------------------------------

def test_extract_wave():
    traces = np.arange(30).reshape((6, 5))
    mask = np.array([0, 1, 1, .5, 0])
    wave_len = 4

    with raises(ValueError):
        _extract_wave(traces, -1, mask, wave_len)

    with raises(ValueError):
        _extract_wave(traces, 20, mask, wave_len)

    ae(_extract_wave(traces, 0, mask, wave_len)[0],
       [[0, 0, 0], [0, 0, 0], [1, 2, 3], [6, 7, 8]])

    ae(_extract_wave(traces, 1, mask, wave_len)[0],
       [[0, 0, 0], [1, 2, 3], [6, 7, 8], [11, 12, 13]])

    ae(_extract_wave(traces, 2, mask, wave_len)[0],
       [[1, 2, 3], [6, 7, 8], [11, 12, 13], [16, 17, 18]])

    ae(_extract_wave(traces, 5, mask, wave_len)[0],
       [[16, 17, 18], [21, 22, 23], [0, 0, 0], [0, 0, 0]])


#------------------------------------------------------------------------------
# Test views
#------------------------------------------------------------------------------

def test_waveform_view(qtbot):
    n_spikes = 20
    n_samples = 30
    n_channels = 40
    n_clusters = 3

    waveforms = artificial_waveforms(n_spikes, n_samples, n_channels)
    masks = artificial_masks(n_spikes, n_channels)
    spike_clusters = artificial_spike_clusters(n_spikes, n_clusters)
    channel_positions = staggered_positions(n_channels)

    # Create the view.
    v = WaveformView(waveforms=waveforms,
                     masks=masks,
                     spike_clusters=spike_clusters,
                     channel_positions=channel_positions,
                     )
    # Select some spikes.
    spike_ids = np.arange(5)
    cluster_ids = np.unique(spike_clusters[spike_ids])
    v.on_select(cluster_ids, spike_ids)

    # Show the view.
    v.show()
    qtbot.waitForWindowShown(v.native)

    # Select other spikes.
    spike_ids = np.arange(2, 10)
    cluster_ids = np.unique(spike_clusters[spike_ids])
    v.on_select(cluster_ids, spike_ids)

    # qtbot.stop()
    v.close()


def test_trace_view_no_spikes(qtbot):
    n_samples = 1000
    n_channels = 12
    sample_rate = 2000.

    traces = artificial_traces(n_samples, n_channels)

    # Create the view.
    v = TraceView(traces=traces, sample_rate=sample_rate)
    _show(qtbot, v)


def test_trace_view_spikes(qtbot):
    n_samples = 1000
    n_channels = 12
    sample_rate = 2000.
    n_spikes = 20
    n_clusters = 3

    traces = artificial_traces(n_samples, n_channels)
    spike_times = artificial_spike_samples(n_spikes) / sample_rate
    # spike_times = [.1, .2]
    spike_clusters = artificial_spike_clusters(n_spikes, n_clusters)
    masks = artificial_masks(n_spikes, n_channels)

    # Create the view.
    v = TraceView(traces=traces,
                  sample_rate=sample_rate,
                  spike_times=spike_times,
                  spike_clusters=spike_clusters,
                  masks=masks,
                  n_samples_per_spike=6,
                  )
    _show(qtbot, v)
