import plotly.colors as colors
from .figure_methods import Figure_Methods
from .widget_container import WidgetContainer
from IPython.display import display
import numpy as np

# from subcutaneous import _callableSync


class _Plots:
	DEFAULT_COLORS = colors.DEFAULT_PLOTLY_COLORS
	LEN_DEFAULT_COLORS = len(DEFAULT_COLORS)

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
		# if fig_functions:
		# 	for k, v in fig_functions.items():
		# 		func = getattr(fig, k)	# [1.XXX] Cant remember why we can pull it from the fig
		# 		func = _callableSync(func, locals())

		# 		func(v, **kwargs)

		# if functions:
		# 	for k, v in functions.items():
		# 		func = getattr(fig, k)	# [1.XXX]
		# 		func = _callableSync(func, locals())
		# 		func(fig, v, **kwargs)

		if display_graph:
			if fig_type == "Widget":
				_container = graph_parameters.get("container", None)
				_container = _container(fig)
				if isinstance(_container, WidgetContainer):
					display(_container.container)
				else:
					display(_container)
				fig = _container

			else:
				fig.show()

		return fig

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
