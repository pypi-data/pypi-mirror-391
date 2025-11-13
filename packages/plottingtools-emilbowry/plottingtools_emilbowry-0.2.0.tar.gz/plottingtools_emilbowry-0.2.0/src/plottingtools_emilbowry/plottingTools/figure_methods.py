from subcutaneous import container
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .trace_methods import Trace_Methods
from plotly.basedatatypes import BaseTraceType


def concatenateTraces(*_traces):
	new_arr = np.dstack(np.array((*_traces,), dtype=object))
	return new_arr.tolist()


def formatTraceItem(item):
	if isinstance(item, (list, np.ndarray)):
		item = np.hstack(item)
	return np.array(item).tolist()


@container
class Figure_Methods:

	def flattenHetrogenous(traces):

		if np.ndim(np.array(traces, dtype=object)) == 0:
			return traces
		elif np.ndim(np.array(traces, dtype=object)) == 1:
			return list(traces)
		else:
			temp = []
			for row in traces:
				for col in row:
					temp.append(formatTraceItem(col))

			return np.fromiter(temp, dtype=object)

	def formatHetrogenous(traces):
		arr = np.array(traces, dtype=object)
		if arr.size > 0:

			if np.ndim(arr) == 1:
				pass
			else:
				for r in range(np.ndim(arr)):
					arr = np.hstack(arr)
			try:
				return arr[arr != None]
			except Exception as e:
				raise Exception(f"{arr}")
		return None

	def getFigureSize(traces):
		if isinstance(traces, BaseTraceType):
			return 1
		f = Figure_Methods.flattenHetrogenous(traces)
		flat = [i[0] if isinstance(i, (list, np.ndarray)) else i for i in f]
		arr = np.array(flat)
		size = np.size(arr[arr != None])
		return size

	def initialiseFigure(traces, *, fig_parameters, **kwargs):

		size = Figure_Methods.getFigureSize(traces)
		if size > 1:
			subplot_parameters = fig_parameters
			fig_parameters = dict()
		fig = go.Figure(data=[None] * size, skip_invalid=True, **fig_parameters)
		if size > 1:
			dimensions = [len(traces), len(traces[0])]
			rows = (dimensions[0:1] or [1])[0]
			cols = (dimensions[1:2] or [1])[0]
			fig = make_subplots(figure=fig, rows=rows, cols=cols, **subplot_parameters)

		return fig

	def addOrphans(fig, orphans):
		orphans = Figure_Methods.formatHetrogenous(orphans)
		if np.size(np.array(orphans, dtype=object)) == 0:
			return fig
		if orphans is None:
			return fig

		fig.add_traces(orphans.tolist())

		return fig

	def processEmpty(fig, *args, idx, **kwargs):
		orphaned = []
		fig = Trace_Methods.expand_y(fig, idx - 1)
		return fig, orphaned

	def processLayout(fig, flat_traces, idx, *args, **kwargs):
		orphaned = []
		for i, trace in enumerate(flat_traces):
			fig, orphans = Figure_Methods.modifyFigure(fig, trace, idx=i + idx, **kwargs)
			orphaned.extend(orphans)
		return fig, orphaned

	def processOverlays(fig, flat_traces, idx, *args, **kwargs):
		orphaned = []
		trace = flat_traces[0]
		fig, orphans = Figure_Methods.modifyFigure(fig, trace, idx=idx, **kwargs)
		orphaned.extend(orphans)
		_ophans = flat_traces[1:]	# [NOTE] unformatted hence _ prefix
		for o in list(_ophans):
			if o is not None:
				orphaned.append(Trace_Methods.formatOrphan(o, idx=idx))
		return fig, orphaned

	def processSingleTrace(fig, flat_traces, idx, *args, **kwargs):
		orphaned = []	# [NOTE] for interface similarity
		fig = Trace_Methods.addTrace(fig, flat_traces, idx=idx, **kwargs)
		return fig, orphaned

	def modifyFigure(fig, flat_traces, idx=0, *args, **kwargs):
		if isinstance(flat_traces, BaseTraceType):
			fig, orphaned = Figure_Methods.processSingleTrace(fig, flat_traces, idx, **kwargs)
		elif isinstance(flat_traces, list):
			fig, orphaned = Figure_Methods.processOverlays(fig, flat_traces, idx, **kwargs)
		elif isinstance(flat_traces, np.ndarray):
			fig, orphaned = Figure_Methods.processLayout(fig, flat_traces, idx, **kwargs)
		elif flat_traces is None:
			fig, orphaned = Figure_Methods.processEmpty(fig, flat_traces, idx=idx, **kwargs)
		else:
			raise TypeError(f"Unknown Trace Type: {type(flat_traces)} | Trace: {flat_traces}")
		if orphaned == []:
			return fig, [None]
		return fig, orphaned

	def generateFigure(traces, fig_parameters, fig_type, **kwargs):
		fig = Figure_Methods.initialiseFigure(traces, fig_parameters=fig_parameters, **kwargs)

		flat_traces = Figure_Methods.flattenHetrogenous(traces)

		with fig.batch_update():

			fig, orphans = Figure_Methods.modifyFigure(fig, flat_traces, **kwargs)
			fig = Figure_Methods.addOrphans(fig, orphans)

			if fig_type == "Widget":
				fig = go.FigureWidget(fig)
		return fig
