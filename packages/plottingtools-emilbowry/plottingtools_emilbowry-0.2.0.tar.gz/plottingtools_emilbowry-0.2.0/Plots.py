import ipywidgets as widgets
from IPython.display import display
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as colors
import plotly.io as pio

pio.renderers.default = "notebook"
import numpy as np


def interface_required(func):
	def _wrapper(*args, **kwargs):
		try:
			import Interface

		except ImportError:
			raise ImportError("Interface module is required for this functionality.")
		return func(*args, **kwargs)

	return _wrapper


class Plots:

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

	def _callableSync(obj, update_dict):
		if getattr(obj, "_callable", False):

			args = getattr(obj, "_args", ())
			kwds = getattr(obj, "_kwargs", dict()).copy()

			shared = set(kwds) & set(update_dict)
			for k in shared:
				kwds[k] = update_dict[k]
			return obj(args, **kwds)
		return obj

	def createGraph(graph_parameters, display_graph=True, **kwargs):
		"""
		graph_parameters={
		                                "traces":trace_list,# trace_list.shape = rows,cols
		                                "layout":layout_dict,
		                                "fig_type":fig_type_str,
		                                "fig_parameters":dict|None
		                                "fig_functions":{"function_name":"parameters"}
		                                **optional_parameters
		                                }

		"""
		graph_parameters.update(**kwargs)

		traces = np.array(graph_parameters["traces"], dtype=object)

		functions = graph_parameters.get("functions", None)
		fig_functions = graph_parameters.get("fig_functions", None)
		fig_type = graph_parameters.get("fig_type", None)
		fig_parameters = graph_parameters.get("fig_parameters", dict())
		subplots = np.shape(traces) != tuple() and np.shape(traces)[0] >= 1	# fixed

		if subplots:
			dimensions = [len(traces), len(traces[0])]

			rows = (dimensions[0:1] or [1])[0]
			cols = (dimensions[1:2] or [1])[0]
			fig = make_subplots(rows=rows, cols=cols, **fig_parameters)

			if fig_type == "Widget":
				container = graph_parameters.get("container", None)
				if container is None:
					raise ValueError("Widget expects a base")

				fig = go.FigureWidget(fig)

			for i in range(rows):
				for j in range(cols):
					trace = graph_parameters["traces"][i][j]
					if trace is not None:
						if isinstance(trace, list):
							[fig.add_trace(t, row=i + 1, col=j + 1) for t in trace if t is not None]
						else:
							# print(i,j)

							# print(trace)
							fig.add_trace(trace, row=i + 1, col=j + 1)

		else:
			fig = go.Figure(**fig_parameters)
			if graph_parameters["traces"] is not None:

				fig.add_trace(graph_parameters["traces"])

		fig.update_layout(graph_parameters["layout"])

		if fig_functions:
			for k, v in fig_functions.items():
				func = getattr(fig, k)
				func = Plots._callableSync(func, locals())

				func(v, **kwargs)

		if functions:
			for k, v in functions.items():
				func = getattr(fig, k)
				# func = _callableSync(func,locals())
				func(fig, v, **kwargs)
		if display_graph:
			if fig_type == "Widget":
				container = Plots._callableSync(container, locals())(fig)
				display(container)
			else:
				fig.show()
		return fig

	@staticmethod
	def graphVariational(data, **kwargs):

		def getKwargVars(**kwargs):

			alpha_name = kwargs["alpha_name"] if "alpha_name" in kwargs else "alpha"

			beta_name = kwargs["beta_name"] if "beta_name" in kwargs else "beta"

			function_name = kwargs["function_name"] if "function_name" in kwargs else "function"

			alpha_range = (
				kwargs["alpha_range"] if "alpha_range" in kwargs else (0, alpha_len - 1)
			)
			beta_range = kwargs["beta_range"] if "beta_range" in kwargs else (0, beta_len - 1)
			return alpha_name, beta_name, alpha_range, beta_range, function_name

		dimensions = np.shape(data)
		# parameters=parameters[0][0]
		if dimensions[0] > 2:
			_matrix = data
		else:
			raise

		alpha_len, beta_len = len(_matrix), len(_matrix[0])
		alpha_name, beta_name, alpha_range, beta_range, function_name = getKwargVars(**kwargs)

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

		scatter = go.Scatter(x=x, y=matrix[beta_idx, alpha_idx], mode="lines")

		camera = dict(
			eye=dict(x=-1.8, y=-1.8, z=1.0),
			up=dict(x=0.0, y=0.0, z=1.0),
			center=dict(x=0.0, y=0.0, z=0.0),
		)
		fig_parameters = dict(
			specs=[
				[{"type": "surface"}, {"type": "surface"}],
				[{"colspan": 2, "type": "xy"}, None],
			],
			vertical_spacing=0.08,
			row_heights=[0.75, 0.25],
		)

		layout = dict(
			width=1400,
			height=850,
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

		def container(fig, **kwargs):

			# alpha_name, beta_name, func_name = updateSliderNames(**kwargs)

			def _idx(val, grid):
				return int(round((val - grid[0]) / (grid[1] - grid[0])))

			alpha_slider = widgets.FloatSlider(
				value=float(Alpha[alpha_idx]),
				min=float(Alpha.min()),
				max=float(Alpha.max()),
				step=float(Alpha[1] - Alpha[0]),
				description=f"{alpha_name}",
				continuous_update=False,
			)

			beta_slider = widgets.FloatSlider(
				value=float(Beta[beta_idx]),
				min=float(Beta.min()),
				max=float(Beta.max()),
				step=float(Beta[1] - Beta[0]),
				description=f"{beta_name}",
				continuous_update=False,
			)

			def refresh(_=None):
				i = _idx(beta_slider.value, Beta)	# current beta index
				j = _idx(alpha_slider.value, Alpha)	# current alpha index

				with fig.batch_update():
					fig.data[0].z = matrix[i]

					fig.data[1].z = matrix[:, j]

					# 1‑D line
					fig.data[2].y = matrix[i, j]

					fig.layout.title.text = (
						f"{function_name} –  {alpha_name} = {Alpha[j]:.2f}, " f"{function_name} = {Beta[i]:.2f}"
					)

			alpha_slider.observe(refresh, names="value")
			beta_slider.observe(refresh, names="value")
			controls = widgets.VBox(
				[alpha_slider, beta_slider], layout=widgets.Layout(width="100%")
			)
			container = widgets.VBox([controls, fig], layout=widgets.Layout(width="100%"))

			return container

		graph_parameters = {
			"traces": [[alpha_surface, beta_surface], [scatter, None]],
			"layout": layout,
			"fig_type": "Widget",
			"fig_parameters": fig_parameters,
			"container": container,
		}
		return graph_parameters

	@staticmethod
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
			if globals().get("Data", None) is None:
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
	def pulseLocation(y_data):
		y = y_data
		y = np.array(y)
		x = np.arange(len(y), dtype=np.float32)
		dy = np.diff(y, prepend=y[0])
		a = (np.cumsum(x * dy) + x * dy) / len(y)
		b = np.diff(a, prepend=a[0] - (a[1] - a[0]) / 2)
		indices = np.where(np.abs(b) > 0.66 * np.abs(y))

		return indices[0], b, a

	PLOT_MAPPING = {
		0: graphScatter,
		1: NotImplemented,
		2: graphHistogram,
		3: graphVariational,
	}
