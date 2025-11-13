import ipywidgets as widgets
from IPython.display import display
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as colors
import plotly.io as pio

from plotly.basedatatypes import BaseTraceType

pio.renderers.default = "notebook"
import numpy as np


def container(cls):
	def new(obj, *args, **kwargs):
		raise NotImplementedError(f"{obj} is a container, __new__ is not defined")

	def init(obj, *args, **kwargs):
		raise NotImplementedError(f"{obj} is a container, __init__ is not defined")

	def call(obj, *args, **kwargs):
		raise NotImplementedError(f"{obj} is a container, __call__ is not defined")

	for name, member in list(cls.__dict__.items()):
		if callable(member):
			setattr(cls, name, staticmethod(member))
	setattr(cls, "__new__", new)
	setattr(cls, "__init__", init)
	setattr(cls, "__call__", call)

	return cls


def _callableSync(obj, update_dict):
	if getattr(obj, "_callable", False):

		# allow assigining params as attributes for simple interfacing
		args = getattr(obj, "_args", ())
		kwds = getattr(obj, "_kwargs", dict()).copy()

		shared = set(kwds) & set(update_dict)
		for k in shared:
			kwds[k] = update_dict[k]
		return obj(*args, **kwds)
	return obj


class widgetContainer:
	def meta(self, *args, **kwds):
		return type(*args, **kwds)

	def tagged(self, *args, _id, **kwds):
		my_id = _id
		owner = self

		class tagged(metaclass=owner.meta):
			identifier = my_id

			def __new__(cls, *args, **kwds):
				instance = object.__new__(cls)
				return instance

			def __init__(self, _function):
				self.func = _function
				owner.updateFunctions.append(self.func)

			def __call__(self, *args, **kwargs):
				self.func(*args, **kwargs)
				owner.computeAux(my_id, *args, **kwargs)

		return tagged


class sliderContainer(widgetContainer):
	@staticmethod
	def _idx(val, data):
		return int(round((val - data[0]) / (data[1] - data[0])))

	@staticmethod
	def _closedIdx(data):
		def _inner(val):
			return sliderContainer._idx(val, data)

		return _inner

	@staticmethod
	def createSlider(*, value, _min, _max, step, description, continuous_update, **kwargs):
		slider = widgets.FloatSlider(
			value=value,
			min=_min,
			max=_max,
			step=step,
			description=description,
			continuous_update=continuous_update,
		)

		return slider

	def _createSlider(self, _slider_dict, **kwargs):
		slider_name = list(_slider_dict.keys())[0]
		slider_dict = list(_slider_dict.values())[0]
		slider_data = slider_dict["data"]
		creation_dict = dict(
			value=float(slider_data[0]),
			_min=float(slider_data.min()),
			_max=float(slider_data.max()),
			step=float(slider_data[1] - slider_data[0]),
			description=f"{slider_name}",
			continuous_update=slider_dict.get("continuous_update", False),
		)
		creation_dict.update(**kwargs)

		slider = sliderContainer.createSlider(**creation_dict)

		self.Sliders[slider_name] = slider
		self.Slider_idxFn[slider_name] = sliderContainer._closedIdx(slider_data)
		self.Sliders[slider_name].observe(self.refresh, names="value")

	@property
	def sliders(self):
		return list(self.Sliders.values())

	def __init__(self, slider_dicts, update_functions, data, **kwargs):

		self.Sliders = dict()
		self.Slider_idxFn = dict()
		self.auxilliary = dict()

		for i in slider_dicts:
			self._createSlider(i)
		for k, v in kwargs.items():
			setattr(self, k, v)
		self.updateFunctions = update_functions	# list probably
		self.data = data

	def _refreshSliders(self, *args, **kwargs):
		slider_indices = dict()
		Slider_Values = dict()
		for k, v in self.Sliders.items():
			value = v.value
			slider_indices[k] = self.Slider_idxFn[k](value)
			Slider_Values[k] = value
		return slider_indices, Slider_Values

	def _updateFigure(self, slider_indices, values, *args, **kwargs):

		for fn in self.updateFunctions:
			fn(
				fig=self.fig,
				data=self.data,
				slider_indices=slider_indices,
				values=values,
				*args,
				**kwargs,
			)

	def refresh(self, *args, **kwargs):
		slider_indices, Slider_Values = self._refreshSliders(*args, **kwargs)
		with self.fig.batch_update():
			self._updateFigure(slider_indices, Slider_Values)

	def __call__(self, fig):
		self.fig = fig

		for i in fig.data:
			if hasattr(i, "meta") and i.meta is not None:
				if "id" in i.meta:
					self.auxilliary[i.meta["id"]] = {"index": fig.data.index(i)}
				if "axis" in i.meta:
					self.auxilliary[i.meta["id"]]["axis"] = i.meta["axis"]
				if "data_idx" in i.meta:
					self.auxilliary[i.meta["id"]]["data_idx"] = i.meta["data_idx"]
				for k, v in i.meta.items():
					if k not in self.auxilliary[i.meta["id"]]:
						self.auxilliary[i.meta["id"]][k] = v
		self.controls = widgets.VBox(self.sliders)	# , layout=widgets.Layout(width="100%")
		self.container = widgets.VBox([self.controls, self.fig])
		return self

	def computeAux(self, _id, *, data, slider_indices, values, **kwargs):
		aux = self.auxilliary[_id]
		idx = aux["index"]
		_data_idx = aux["data_idx"]
		ax = aux["axis"]
		data_idx = []
		for i in _data_idx:
			if isinstance(i, str):
				if i == "__SLICE__":
					data_idx.append(i)
					data_idx[-1] = slice(None)
				else:
					v = slider_indices[i]
					data_idx.append(v)
			else:
				data_idx.append(i)

		self.fig.data[idx][ax] = data[tuple(data_idx)]


@container
class Trace_Methods:
	def getSuffix(idx):
		axis_idx = ""
		if idx == 0:
			return axis_idx
		return str(idx + 1)

	def getTraceIndex(row, col, n_cols):
		return (row - 1) * n_cols + (col - 1)

	def expand_y(fig, idx):
		suffix = Trace_Methods.getSuffix(idx)
		x_domain = fig.layout[f"xaxis{suffix}"]["domain"]

		diff = x_domain[1] - x_domain[0]
		new_dom = (x_domain[0], x_domain[1] + diff)
		fig._layout[f"xaxis{suffix}"].update({"domain": new_dom})
		return fig

	def inverseTraceIndex(index, n_cols):
		_row = index // n_cols	# [NOTE] actual row is _row +1
		_col = index % n_cols	# [NOTE] actual col is _col +1
		return _row, _col

	def updateFigure(fig, trace, idx, *args, expand_col=False, **kwargs):
		suffix = Trace_Methods.getSuffix(idx)

		if "z" in trace:
			trace._orphan_props["scene"] = f"scene{suffix}"

			if fig._grid_ref:

				try:
					n_cols = len(fig._grid_ref[0])
					row, col = Trace_Methods.inverseTraceIndex(idx, n_cols)
					if not fig._grid_ref[row][col][0].subplot_type == "scene":
						# [NOTE] using NotImplementedError as a low probability of intercept raise
						raise NotImplementedError

				except NotImplementedError as e:

					y_domain = fig.layout[f"yaxis{suffix}"]["domain"]
					x_domain = fig.layout[f"xaxis{suffix}"]["domain"]

					scene = {
						"domain": {"x": x_domain, "y": y_domain, "column": col + 1, "row": row + 1}
					}

					# fig._layout[f"scene{suffix}"] = scene
					fig._layout.update(({f"scene{suffix}": scene}))

					# [NOTE]  The figure attributes `yaxis{suffix}` and `xaxis{suffix}` don't need to be kept to preserve indexing
					# fig.layout.pop(f"yaxis{suffix}", None)
					# fig.layout.pop(f"xaxis{suffix}", None)

		fig._data[idx] = trace._orphan_props
		for k, v in trace._orphan_props.items():
			try:
				fig._data[idx][k] = v	# trace._orphan_props
				fig.data[idx][k] = v	# trace._orphan_props

			except:
				pass
		return fig

	def formatOrphan(orphan, idx):
		suffix = Trace_Methods.getSuffix(idx)
		orphan_update = dict()

		if "z" in orphan:
			orphan_update.update({"scene": f"scene{suffix}"})
		else:

			orphan_update = {"xaxis": f"x{suffix}", "yaxis": f"y{suffix}"}

		orphan._orphan_props.update(orphan_update)
		return orphan

	def appendData(fig, data, idx, *args, **kwargs):

		for k, v in data.items():
			if k.endswith("axis"):
				fig._data[idx][k] = v	# [NOTE] Manipulate `_data` so propagated to widgets too
			elif k != "uid":
				if k == ("x" or "y" or "z"):

					_data = getattr(fig.data[idx], k, [])
					if _data is None:
						_data = []
					_data = list(_data)

					_data.extend(v)
					fig._data[idx][k] = _data
			else:

				fig._data[idx][k] = v
				fig.data[idx][k] = v

		return fig

	def addTrace(fig, trace, idx, *args, _modification_type="append", **kwargs):
		suffix = Trace_Methods.getSuffix(idx)

		target_trace = fig.data[idx]
		if target_trace.type != trace.type:
			fig = Trace_Methods.updateFigure(fig, trace, idx, *args, **kwargs)
		else:
			data = {"x": trace.x, "y": trace.y}
			if "z" in trace:
				data["z"] = trace["z"]
			data.update({"xaxis": f"x{suffix}", "yaxis": f"y{suffix}"})

			if "uid" in trace:

				data["uid"] = trace["uid"]

			for k, v in dict(vars(trace)).items():
				if k not in data:
					data[k] = v
			if _modification_type == "append":

				fig = Trace_Methods.appendData(fig, data, idx, *args, **kwargs)

		return fig


@container
class Figure_Methods:

	def concatenateTraces(*_traces):
		new_arr = np.dstack(np.array((*_traces,), dtype=object))
		return new_arr.tolist()

	def formatTraceItem(item):
		if isinstance(item, (list, np.ndarray)):
			item = np.hstack(item)
		return np.array(item).tolist()

	def flattenHetrogenous(traces):

		if np.ndim(np.array(traces, dtype=object)) == 0:
			return traces
		elif np.ndim(np.array(traces, dtype=object)) == 1:
			return list(traces)
		else:
			temp = []
			for row in traces:
				for col in row:
					temp.append(Figure_Methods.formatTraceItem(col))

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


class _Plots:
	DEFAULT_COLORS = colors.DEFAULT_PLOTLY_COLORS
	LEN_DEFAULT_COLORS = len(DEFAULT_COLORS)

	@staticmethod
	def histogram(func):
		func.plot = 2	# hello
		return func

	@staticmethod
	def scatter(func):
		func.plot = 0
		return func

	@staticmethod
	def variations(func):
		func.plot = 3
		return func

	@staticmethod
	def createGraph(graph_parameters, display_graph=True, **kwargs):

		traces = graph_parameters["traces"]
		fig_parameters = graph_parameters.get("fig_parameters", dict())
		fig_type = graph_parameters.get("fig_type", None)
		layout = graph_parameters.get("layout", dict())

		fig = Figure_Methods.generateFigure(traces, fig_parameters, fig_type, **kwargs)

		fig.update_layout(layout)

		functions = graph_parameters.get("functions", None)
		fig_functions = graph_parameters.get("fig_functions", None)
		if fig_functions:
			for k, v in fig_functions.items():
				func = getattr(fig, k)	# [1.XXX] Cant remember why we can pull it from the fig
				func = _callableSync(func, locals())

				func(v, **kwargs)

		if functions:
			for k, v in functions.items():
				func = getattr(fig, k)	# [1.XXX]
				func = _callableSync(func, locals())
				func(fig, v, **kwargs)

		if display_graph:
			if fig_type == "Widget":
				_container = graph_parameters.get("container", None)
				_container = _container(fig)
				if isinstance(_container, widgetContainer):
					display(_container.container)
				else:
					display(_container)

			else:
				fig.show()

		return fig

	@staticmethod
	def graphScatter(data, *, normalise_x_axis=False, **kwargs):
		Y = data[0]
		try:
			X = data[1]
		except:
			X = list(range(len(Y)))
		if X is None:
			X = list(range(len(Y)))

		trace = go.Scatter(x=X, y=Y, **kwargs)

		layout = dict(
			barmode="overlay",
			bargap=0,
		)
		graph_parameters = {
			"traces": trace,
			"layout": layout,
		}

		return graph_parameters

	@staticmethod
	def variational_getKwargVars(alpha_len, beta_len, **kwargs):

		alpha_name = kwargs["alpha_name"] if "alpha_name" in kwargs else "alpha"

		beta_name = kwargs["beta_name"] if "beta_name" in kwargs else "beta"

		function_name = kwargs["function_name"] if "function_name" in kwargs else "function"

		alpha_range = kwargs["alpha_range"] if "alpha_range" in kwargs else (0, alpha_len - 1)
		beta_range = kwargs["beta_range"] if "beta_range" in kwargs else (0, beta_len - 1)
		return alpha_name, beta_name, alpha_range, beta_range, function_name

	@staticmethod
	def pulseLocation(y_data):
		y = y_data
		y = np.array(y)
		x = np.arange(len(y), dtype=np.float32)
		dy = np.diff(y, prepend=y[0])
		a = (np.cumsum(x * dy) + x * dy) / len(y)
		b = np.diff(a, prepend=a[0] - (a[1] - a[0]) / 2)
		# indices = np.where(np.abs(b / y) > 0.75)[0]
		indices = np.where(np.abs(b) > 0.66 * np.abs(y))

		return indices[0], b, a

	@staticmethod
	def formatName(string):
		count = 0
		_idx = -1
		arr = list(string)
		for i, c in enumerate(string):
			condition_1 = c.lower() != c or c.isdigit()
			condition_3 = _idx >= i - 1
			if condition_1 and condition_3:
				_idx = i
			elif condition_1 or condition_3:
				_idx = i - 1
				if i > 1:
					count += 1
					arr.insert(count + _idx, "_")
		string = "".join(arr).lower()

		return string

	@staticmethod
	def plots(cls):

		plot_logic_functions = [
			(name, func)
			for name, func in vars(cls).items()
			if callable(func) and not name.startswith("__")
		]
		for plot_logic_name, plot_logic_func in plot_logic_functions:

			def make_setter(plot_logic_func):
				def setter(func_to_decorate):
					func_to_decorate.plotter = plot_logic_func
					return func_to_decorate

				return setter

			if plot_logic_name.startswith("graph"):
				plot_logic_name = plot_logic_name[5:]
			setter_name = _Plots.formatName(plot_logic_name)

			setattr(cls, setter_name, make_setter(plot_logic_func))

		return cls


@_Plots.plots
class Plots(_Plots):

	def graphVariational(data, **kwargs):

		dimensions = np.shape(data)
		if dimensions[0] > 2:
			_matrix = data
		else:
			raise

		alpha_len, beta_len = len(_matrix), len(_matrix[0])
		alpha_name, beta_name, alpha_range, beta_range, function_name = (
			_Plots.variational_getKwargVars(alpha_len, beta_len, **kwargs)
		)

		matrix = np.stack(_matrix.tolist())	# beta × alpha × T

		ymax = np.max(_matrix.tolist())
		X = matrix[0][0].shape[0]

		x = np.arange(X)

		Alpha = np.linspace(*alpha_range, alpha_len)

		Beta = np.linspace(*beta_range, beta_len)

		Xalpha, Yalpha = np.meshgrid(x, Alpha)	# left surface  (beta fixed)
		Xbeta, Ybeta = np.meshgrid(x, Beta)	# right surface (alpha fixed)

		beta_idx, alpha_idx = 0, 0

		alpha_surface = go.Surface(
			z=matrix[beta_idx],
			x=Xalpha,
			y=Yalpha,
			colorscale="Viridis",
			cmin=0,
			cmax=ymax,
			showscale=True,
		)

		beta_surface = go.Surface(
			z=matrix[:, alpha_idx],
			x=Xbeta,
			y=Ybeta,
			colorscale="Viridis",
			cmin=0,
			cmax=ymax,
			showscale=True,
		)

		scatter = go.Scatter(
			x=x,
			y=matrix[beta_idx, alpha_idx],
			mode="lines",	# uid="h"
		)

		camera = dict(
			eye=dict(x=-1.8, y=-1.8, z=1.0),
			up=dict(x=0.0, y=0.0, z=1.0),
			center=dict(x=0.0, y=0.0, z=0.0),
		)
		fig_parameters = dict(
			specs=[	# [TODO] Remove Specs since it is infereable now
				[{"type": "surface"}, {"type": "surface"}],
				[{"colspan": 2, "type": "xy"}, None],
			],
			vertical_spacing=0.08,
			row_heights=[0.75, 0.25],
		)

		layout = dict(
			width=1800,
			height=1000,
			scene=dict(
				xaxis_title="x",
				yaxis_title=f"{alpha_name}",
				zaxis_title=f"{function_name}",
				camera=camera,
			),
			scene2=dict(
				xaxis_title="x",
				yaxis_title=f"{beta_name}",
				zaxis_title=f"{function_name}",
				camera=camera,
			),
		)

		def beta_update(*, fig, slider_indices, data, **kwargs):
			i = slider_indices[f"{beta_name}"]
			fig.data[0].z = data[i]

		def alpha_update(*, fig, slider_indices, data, **kwargs):
			j = slider_indices[f"{alpha_name}"]

			fig.data[0].z = data[:, j]

		def timeseries_update(*, fig, slider_indices, data, **kwargs):
			i = slider_indices[f"{beta_name}"]
			j = slider_indices[f"{alpha_name}"]

			fig.data[2].y = data[i, j]

		def title_update(*args, fig, values, **kwargs):
			beta_val = values[f"{beta_name}"]
			alpha_val = values[f"{alpha_name}"]

			_function_name = kwargs.get("function_name", f"{function_name}")

			fig.layout.title.text = (
				f"{_function_name} –  {alpha_name} = {alpha_val:.2f}, " f"{beta_name} = {beta_val:.2f}"
			)

		update_fns = [beta_update, alpha_update, timeseries_update, title_update]
		alpha_slider_dict = {f"{alpha_name}": {"data": Alpha}}
		beta_slider_dict = {f"{beta_name}": {"data": Beta}}
		slider_dicts = [beta_slider_dict, alpha_slider_dict]
		wContainer = sliderContainer(slider_dicts, update_fns, matrix)

		graph_parameters = {
			"traces": [[alpha_surface, beta_surface], [scatter, None]],
			"layout": layout,
			"fig_type": "Widget",
			"fig_parameters": fig_parameters,	# Not strictly necessary for specs
			"container": wContainer,
		}
		return graph_parameters

	def graphHistogram(
		data,
		*,
		mode="bar",
		normalise_x_axis=False,
		density=False,
		**kwargs,
	):

		counts = data[0]
		midpoints = data[1]
		if len(midpoints) == len(counts) + 1:
			# Assume data[1[ is bin edges
			midpoints = (midpoints[:-1] + midpoints[1:]) / 2
			# midpoints = midpoints[:-1]
		if normalise_x_axis:
			Data = globals().get("Data", None)
			if Data is None:
				print(
					"Data module not imported. Please import Data module to use normalise function."
				)
				midpoints = (midpoints - midpoints.min()) / (midpoints.max() - midpoints.min())
			else:
				midpoints = Data.normalise(midpoints)
		if density:
			counts = counts / np.sum(counts)
		if mode == "bar":
			trace = go.Bar(x=midpoints, y=counts)
		if mode == "scatter":
			trace = go.Scatter(
				x=midpoints,
				y=counts,
				mode="lines",
				line={"shape": "hv"},
			)

		layout = dict(
			barmode="overlay",
			bargap=0,
		)
		graph_parameters = {
			"traces": trace,
			"layout": layout,
		}
		return graph_parameters

	def graphScatter(data, *, normalise_x_axis=False, **kwargs):
		Y = data[0]
		try:
			X = data[1]
		except:
			X = list(range(len(Y)))
		if X is None:
			X = list(range(len(Y)))

		trace = go.Scatter(x=X, y=Y, **kwargs)

		layout = dict(
			barmode="overlay",
			bargap=0,
		)
		graph_parameters = {
			"traces": trace,
			"layout": layout,
		}

		return graph_parameters


@Plots.plots
class PlotsWithCompare(Plots):
	def graphVariationalCompare(
		_data,
		*,
		name_a="Model A",
		name_b="Model B",
		**kwargs,
	):
		data_a = _data[0]
		data_b = _data[1]

		alpha_len, beta_len = len(data_a), len(data_a[0])
		alpha_name, beta_name, alpha_range, beta_range, function_name = (
			Plots.variational_getKwargVars(alpha_len, beta_len, **kwargs)
		)

		aParams = Plots.graphVariational(data_a, **kwargs)

		bParams = Plots.graphVariational(data_b, **kwargs)
		_data = np.array([data_a, data_b])
		cmin = np.minimum(_data.min(), 0)
		cmax = _data.max()
		arr_a = aParams["traces"]
		arr_b = bParams["traces"]

		a0_update_dict = dict(
			name=name_a,
			cmin=cmin,
			cmax=cmax,
			colorbar=dict({"x": -0.2, "len": 0.8}),
		)
		arr_a[0][0]._orphan_props.update(a0_update_dict)
		a1_update_dict = dict(name=name_a, showscale=False)
		arr_a[0][1]._orphan_props.update(a1_update_dict)

		b0_update_dict = dict(
			name=name_b,
			colorscale="Plasma",
			cmin=cmin,
			cmax=cmax,
			opacity=0.5,
			colorbar=dict({"x": -0.1, "len": 0.8}),
		)
		arr_b[0][0]._orphan_props.update(b0_update_dict)

		b1_update_dict = dict(name=name_b, colorscale="Plasma", showscale=False, opacity=0.5)
		arr_b[0][1]._orphan_props.update(b1_update_dict)

		arr_b[0][0].meta = {
			"id": "variational_alpha_surface_b",
			"axis": "z",
			"data_idx": [1, f"{beta_name}"],
		}

		arr_b[0][1].meta = {
			"id": "variational_beta_surface_b",
			"axis": "z",
			"data_idx": [1, "__SLICE__", f"{alpha_name}"],
		}

		arr_b[1][0].meta = {
			"id": "variational_scatter_b",
			"axis": "y",
			"data_idx": [1, f"{beta_name}", f"{alpha_name}"],
		}

		new_traces = Figure_Methods.concatenateTraces(arr_a, arr_b)
		new_params = aParams.copy()
		new_params["traces"] = new_traces

		cont = new_params["container"]
		cont.data = np.array([cont.data, data_b])

		@cont.tagged(_id="variational_alpha_surface_b")
		def beta_update(*, fig, data, slider_indices, **kwargs):
			i = slider_indices[f"{beta_name}"]
			fig.data[0]["z"] = data[(0, i)]

		@cont.tagged(_id="variational_beta_surface_b")
		def alpha_update(*, fig, slider_indices, data, **kwargs):
			j = slider_indices[f"{alpha_name}"]

			fig.data[1].z = data[0][:, j]

		@cont.tagged(_id="variational_scatter_b")
		def timeseries_update(*, fig, slider_indices, data, **kwargs):
			i = slider_indices[f"{beta_name}"]
			j = slider_indices[f"{alpha_name}"]

			fig.data[2]["y"] = data[(0, i, j)]

		def title_update(*, fig, values, **kwargs):
			beta_val = values[f"{beta_name}"]
			alpha_val = values[f"{alpha_name}"]

			_function_name = kwargs.get("function_name", f"{function_name}")

			fig.layout.title.text = (
				f"{_function_name} –  {alpha_name} = {alpha_val:.2f}, " f"{beta_name} = {beta_val:.2f}"
			)

		fig_parameters = dict(
			vertical_spacing=0.08,
			row_heights=[0.70, 0.3],
		)
		update_fns = [beta_update, alpha_update, timeseries_update, title_update]

		cont.updateFunctions = update_fns

		new_params["fig_parameters"] = fig_parameters	# NO SPECS!!!!!! INFEREABLE

		return new_params


def interface(func):

	def _innerInterface(*args, **kwargs):

		result = func(*args, **kwargs)
		params = func.plotter(result)
		Plots.createGraph(params)

		return result

	return _innerInterface


@interface
@PlotsWithCompare.variational_compare
def _test():
	SIZE = 50

	alpha_vals = np.linspace(0.2, 0.8, SIZE)
	beta_vals = np.linspace(5, 25, SIZE)
	x_time = np.linspace(0, 1, SIZE)

	data_a_list = []
	for alpha in alpha_vals:
		row = []
		for beta in beta_vals:
			ramp = 1 / (1 + np.exp(-beta * (x_time - alpha)))
			row.append(ramp)
		data_a_list.append(row)

	data_a = np.array(data_a_list)

	data_b_list = []
	for i in range(SIZE):
		row = []
		for j in range(SIZE):
			modified_ramp = 0.5 * data_a[i, j] + 0.3
			row.append(modified_ramp)
		data_b_list.append(row)
	data_b = np.array(data_b_list)

	return data_a, data_b
