from .plottingTools import _Plots
import numpy as np
import plotly.graph_objects as go
from .plottingTools.widget_container import gridSliderContainer
from .plottingTools import concatenateTraces


def plotter(func):
	def _inner(*args, **kwargs):
		result = func(*args, **kwargs)
		params = func.plotter(result)
		_Plots.createGraph(params)
		return result

	return _inner


@_Plots.plots
class StandardPlots(_Plots):

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
			# specs=[	# [TODO] Remove Specs since it is infereable now
			# 	[{"type": "surface"}, {"type": "surface"}],
			# 	[{"colspan": 2, "type": "xy"}, None],
			# ],
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

			fig.data[1].z = data[:, j]

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
		wContainer = gridSliderContainer(slider_dicts, update_fns, matrix)

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
			midpoints = (midpoints[:-1] + midpoints[1:]) / 2
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

	def graphScatter(data, **kwargs):
		Y = data[0]
		try:
			X = data[1]
		except:
			X = list(range(len(Y)))

		trace = go.Scatter(x=X, y=Y)

		layout = dict(
			barmode="overlay",
			bargap=0,
		)
		graph_parameters = {
			"traces": trace,
			"layout": layout,
		}

		return graph_parameters


@StandardPlots.plots
class PlotsWithCompare(StandardPlots):
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
			StandardPlots.variational_getKwargVars(alpha_len, beta_len, **kwargs)
		)

		aParams = StandardPlots.graphVariational(data_a, **kwargs)

		bParams = StandardPlots.graphVariational(data_b, **kwargs)
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

		new_traces = concatenateTraces(arr_a, arr_b)
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
